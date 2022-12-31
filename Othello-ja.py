import copy
import traceback
import sys
from tkinter import *
from tkinter import ttk

ROW_NUM = 8
STONE_1ST = '●'
STONE_2ND = '○'
STONE_OPPONENT = {
    STONE_1ST: STONE_2ND,
    STONE_2ND: STONE_1ST,
}
FONT_FAMILY = ''
FONT_SIZE = 30
FOREGROUND_COLOR = 'black'
BACKGROUND_COLOR = 'green'

DIRECTIONS = (
    (-1, -1),
    (-1, 0),
    (-1, 1),
    (0, -1),
    (0, 1),
    (1, -1),
    (1, 0),
    (1, 1),
)

EVALUATION_BASE = (
    (45, -11, 4, -1, -1, 4, -11, 45),
    (-11, -16, -1, -3, -3, -1, -16, -11),
    (4, -1, 2, -1, -1, 2, -1, 4),
    (-1, -3, -1, 0, 0, -1, -3, -1),
    (-1, -3, -1, 0, 0, -1, -3, -1),
    (4, -1, 2, -1, -1, 2, -1, 4),
    (-11, -16, -1, -3, -3, -1, -16, -11),
    (45, -11, 4, -1, -1, 4, -11, 45),
)

print('レベルを入力してください (1 ~ 10)')
print('※ レベルが高いほど、処理に時間がかかる場合があります。')
a = int(input())
DEPTH_MAX = a


class BoardUI(ttk.Frame):
    def __init__(self, objTk=None):
        super().__init__(objTk)
        self.player1 = PlayerHuman(
            STONE_1ST, '先手 (あなた)'
        )
        self.player2 = PlayerCpu(
            STONE_2ND, '後手 (CPU)'
        )
        self.init_position_list()
        self.init_disp_list()
        self.display_board()

    def init_position_list(self):
        self.position_list = [[''] * ROW_NUM for i in range(ROW_NUM)]
        self.position_list[ROW_NUM // 2 - 1][ROW_NUM // 2 - 1] = STONE_1ST
        self.position_list[ROW_NUM // 2][ROW_NUM // 2] = STONE_1ST
        self.position_list[ROW_NUM // 2 - 1][ROW_NUM // 2] = STONE_2ND
        self.position_list[ROW_NUM // 2][ROW_NUM // 2 - 1] = STONE_2ND

    def init_disp_list(self):
        self.disp_list = [[''] * ROW_NUM for i in range(ROW_NUM)]
        for x in range(ROW_NUM):
            for y in range(ROW_NUM):
                self.disp_list[x][y] = StringVar()
                self.disp_list[x][y].set('')

    def update_board(self):
        for x in range(ROW_NUM):
            for y in range(ROW_NUM):
                self.disp_list[x][y].set(self.position_list[x][y])

    def display_board(self):
        self.display_var = StringVar()
        self.display_var.set(
            '石を置きたい場所をクリックしてください。'
        )

        info_label = ttk.Label(
            self,
            textvariable = self.display_var,
        )

        info_label.grid(
            row = 0,
            column = 0,
            columnspan = ROW_NUM,
            sticky = (N, S, E, W),
        )

        style = ttk.Style()
        style.theme_use('default')
        style.configure(
            'myButton.TButton',
            font = (FONT_FAMILY, FONT_SIZE),
            foreground = FOREGROUND_COLOR,
            background = BACKGROUND_COLOR,
        )

        for x in range(ROW_NUM):
            for y in range(ROW_NUM):
                button = ttk.Button(
                    self,
                    textvariable = self.disp_list[x][y],
                    style = 'myButton.TButton',
                    command = lambda idx_x = x,
                    idx_y = y: self.on_click_board_cell(idx_x, idx_y),
                )
                button.grid(
                    row = x + 1,
                    column = y,
                    sticky = (N, S, E, W),
                )
        self.grid(
            row = 0,
            column = 0,
            sticky = (N, S, E, W),
        )

        self.update_board()

        for y in range(ROW_NUM):
            self.columnconfigure(y, weight=1)

        self.rowconfigure(0, weight=0)
        for x in range(1, ROW_NUM + 1):
            self.rowconfigure(x, weight=1)

        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)

    def on_click_board_cell(self, idx_x, idx_y):
        if is_othello_end(boardUI=self):
            self.init_position_list()
            self.update_board()
            self.display_var.set(
                '石を置きたい場所をクリックしてください。'
            )
            return

        able_position_list = get_able_position_list(
            self.position_list,
            self.player1.stone,
        )

        if not [idx_x, idx_y] in able_position_list:
            self.display_var.set(
                'この位置には石を打つことができません。'
            )
            return

        try:
            self.position_list = put_stone(
                idx_x,
                idx_y,
                copy.deepcopy(self.position_list),
                self.player1.stone,
            )
            self.update_board()

            if is_othello_end(boardUI = self):
                on_othello_end(boardUI = self)
                return

            if get_able_position_num(self.position_list, self.player2.stone) == 0:
                self.display_var.set(
                    '{0}は石を打てないためパス。石を打ちたい場所をクリックしてください。'.format(
                        self.player2.name
                    )
                )
                return

            self.player2.think(boardUI = self)

        except Exception as e:
            print(traceback.format_exc())


class PlayerBase:
    def __init__(self, stone, name):
        self.stone = stone
        self.name = name


class PlayerHuman(PlayerBase):
    pass


class PlayerCpu(PlayerBase):
    def think(self, boardUI):
        boardUI.display_var.set(
            '{0}思考中...'.format(
                boardUI.player2.name
            )
        )
        pass_num = 0

        while(True):
            x_next, y_next, evaluation = get_next_position(
                boardUI,
                copy.deepcopy(boardUI.position_list),
                boardUI.player2.stone,
                depth=0,
                alpha=-sys.maxsize,
                beta=sys.maxsize,
            )
            boardUI.position_list = put_stone(
                x_next,
                y_next,
                copy.deepcopy(boardUI.position_list),
                boardUI.player2.stone,
            )
            boardUI.update_board()

            if is_othello_end(boardUI):
                on_othello_end(boardUI)
                return

            if get_able_position_num(
                boardUI.position_list, boardUI.player1.stone
                ) > 0:
                break

            pass_num += 1

        if pass_num > 0:
            boardUI.display_var.set(
                '{0}は石を打つ位置がなかったため{1}回パス。石を置きたい場所をクリックしてください。'.format(
                    boardUI.player1.name,
                    pass_num,
                )
            )
        else:
            boardUI.display_var.set(
                '石を置きたい場所をクリックしてください。'
            )


def get_able_position_list(position_list, stone_put):
    able_position_list = []
    for x in range(ROW_NUM):
        for y in range(ROW_NUM):
            if position_list[x][y] != '':
                continue
            num = 0
            for d_x, d_y in DIRECTIONS:
                num += get_turn_over_num(
                    x,
                    y,
                    d_x,
                    d_y,
                    position_list,
                    stone_put,
                )
            if num > 0:
                able_position_list.append([x, y])

    return able_position_list


def get_turn_over_num(x, y, d_x, d_y, position_list, stone_put):
    num = 0
    for i in range(1, ROW_NUM):
        if not (
            0 <= (x + d_x * i) <= ROW_NUM - 1
            ) or not (
                0 <= (y + d_y * i) <= ROW_NUM - 1
                ):
            return 0
        stone = position_list[x + d_x * i][y + d_y * i]
        if stone == '':
            return 0
        elif stone == stone_put:
            return num
        num += 1

    return 0


def put_stone(x, y, position_list, stone_put):
    for d_x, d_y in DIRECTIONS:
        num = get_turn_over_num(
            x, y, d_x, d_y, position_list, stone_put
        )
        if num > 0:
            for i in range(1, num + 1):
                position_list[x + d_x * i][y + d_y * i] = stone_put
    position_list[x][y] = stone_put

    return position_list


def get_able_position_num(position_list, stone_put):
    able_position_list = get_able_position_list(
        position_list,
        stone_put,
    )

    return len(able_position_list)


def get_next_position(boardUI, position_list, stone_put, depth, alpha, beta):
    if get_able_position_num(
        position_list,
        stone_put,
    ) == 0:
        return -1, -1, 0
    able_position_list = get_able_position_list(
        position_list,
        stone_put,
    )
    evaluation_list = []
    for x, y in able_position_list:
        position_list2 = put_stone(
            x,
            y,
            copy.deepcopy(position_list),
            stone_put,
        )
        if depth == DEPTH_MAX or get_able_position_num(
            position_list2,
            STONE_OPPONENT[stone_put],
        ) == 0:
            evaluation_list += [get_evaluation(
                position_list2,
                boardUI.player2.stone,
                )]
        else:
            depth += 1
            x_next, y_next, evaluation = get_next_position(
                boardUI,
                position_list2,
                STONE_OPPONENT[stone_put],
                depth,
                alpha,
                beta,
            )
            evaluation_list += [evaluation]
        if stone_put == boardUI.player1.stone:
            if evaluation_list[-1] < alpha:
                break
            if evaluation_list[-1] < beta:
                beta = evaluation_list[-1]
        else:
            if evaluation_list[-1] > beta:
                break
            if evaluation_list[-1] > alpha:
                alpha = evaluation_list[-1]
    evaluation = 0.0
    idx = 0
    if stone_put == boardUI.player1.stone:
        if len(evaluation_list) > 0:
            idx = evaluation_list.index(min(evaluation_list))
    else:
        if len(evaluation_list) > 0:
            idx = evaluation_list.index(max(evaluation_list))
    evaluation = evaluation_list[idx]
    x_next, y_next = able_position_list[idx]

    return x_next, y_next, evaluation


def get_evaluation(position_list, stone_put):
    evaluation = 0.0
    for x in range(ROW_NUM):
        for y in range(ROW_NUM):
            if position_list[x][y] == stone_put:
                evaluation += EVALUATION_BASE[x][y]
            elif position_list[x][y] == STONE_OPPONENT[stone_put]:
                evaluation -= EVALUATION_BASE[x][y]

    return evaluation


def is_othello_end(boardUI):
    empty_num = 0
    stone_1st_num = 0
    stone_2nd_num = 0
    empty_num, stone_1st_num, stone_2nd_num = get_stone_num(boardUI)
    if empty_num == 0:
        return True
    elif stone_1st_num == 0:
        return True
    elif stone_2nd_num == 0:
        return True
    else:
        return False


def on_othello_end(boardUI):
    empty_num = 0
    stone_1st_num = 0
    stone_2nd_num = 0
    empty_num, stone_1st_num, stone_2nd_num = get_stone_num(boardUI)
    boardUI.display_var.set(
        '{0}の石の数: {1}, {2}の石の数: {3}'.format(
            boardUI.player1.name,
            stone_1st_num,
            boardUI.player2.name,
            stone_2nd_num,
        )
    )

def get_stone_num(boardUI):
    empty_num = 0
    stone_1st_num = 0
    stone_2nd_num = 0
    for x in range(ROW_NUM):
        for y in range(ROW_NUM):
            if boardUI.position_list[x][y] == '':
                empty_num += 1
            elif boardUI.position_list[x][y] == boardUI.player1.stone:
                stone_1st_num += 1
            elif boardUI.position_list[x][y] == boardUI.player2.stone:
                stone_2nd_num += 1

    return empty_num, stone_1st_num, stone_2nd_num


def main():
    objTk = Tk()
    objTk.title('オセロ')
    objTk.geometry('500x500')
    BoardUI(objTk)
    objTk.mainloop()


if __name__ == '__main__':
    main()
