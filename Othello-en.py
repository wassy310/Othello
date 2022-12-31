import copy
import traceback
import sys
from tkinter import *
from tkinter import ttk

# オセロ盤の行数（列数）
ROW_NUM = 8
# 石（先手）
STONE_1ST = '●'
# 石（後手）
STONE_2ND = '○'
# 相手の石
STONE_OPPONENT = {
    STONE_1ST: STONE_2ND,
    STONE_2ND: STONE_1ST,
}
# フォント指定
FONT_FAMILY = ''
FONT_SIZE = 30
# セルの前景色
FOREGROUND_COLOR = 'black'
# セルの背景色
BACKGROUND_COLOR = 'green'

# 検索方向
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

# 各セルの評価値
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

# αβ法による探索の深さ
print('レベルを入力してください (1 ~ 10)')
print('※ レベルが高いほど、処理に時間がかかる場合があります。')
a = int(input())
DEPTH_MAX = a


class BoardUI(ttk.Frame):
    def __init__(self, objTk=None):
        super().__init__(objTk)
        # 先手
        self.player1 = PlayerHuman(
            STONE_1ST, '先手 (あなた)'
        )
        # 後手
        self.player2 = PlayerCpu(
            STONE_2ND, '後手 (CPU)'
        )
        # 石の配置を初期化
        self.init_position_list()
        # 石の配置（表示用）を初期化
        self.init_disp_list()
        # オセロ盤を表示
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
        # 情報表示ラベルの表示内容
        self.display_var = StringVar()
        self.display_var.set(
            '石を置きたい場所をクリックしてください。'
        )

        # 情報表示ラベル
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

        # フォント指定
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

        # 石の配置を画面に反映
        self.update_board()

        # 横方向の引き伸ばし設定
        for y in range(ROW_NUM):
            self.columnconfigure(y, weight=1)

        # 縦方向の引き伸ばし設定
        self.rowconfigure(0, weight=0)  # 情報表示欄
        for x in range(1, ROW_NUM + 1):
            self.rowconfigure(x, weight=1)

        # ウィンドウ自体の引き伸ばし設定
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)

    def on_click_board_cell(self, idx_x, idx_y):
        if is_othello_end(boardUI=self):
            # オセロ終了後にオセロ盤をクリックした場合
            # 石の配置を初期化
            self.init_position_list()
            # 石の配置を画面に反映
            self.update_board()
            self.display_var.set(
                '石を置きたい場所をクリックしてください。'
            )
            return

        # 石が打てる位置（先手）
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
            # 先手の石を打つ
            self.position_list = put_stone(
                idx_x,
                idx_y,
                copy.deepcopy(self.position_list),
                self.player1.stone,
            )
            # 石の配置を画面に反映
            self.update_board()

            if is_othello_end(boardUI = self):
                # オセロ終了時
                on_othello_end(boardUI = self)
                return

            if get_able_position_num(self.position_list, self.player2.stone) == 0:
                # 後手が石を打つ位置がない場合
                self.display_var.set(
                    '{0}は石を打てないためパス。石を打ちたい場所をクリックしてください。'.format(
                        self.player2.name
                    )
                )
                return

            # 後手の局面開始
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
        # 先手がパスした回数
        pass_num = 0

        while(True):
            # αβ法により次手を探索
            x_next, y_next, evaluation = get_next_position(
                boardUI,
                copy.deepcopy(boardUI.position_list),
                boardUI.player2.stone,
                depth=0,
                alpha=-sys.maxsize,
                beta=sys.maxsize,
            )
            # 後手の石を打つ
            boardUI.position_list = put_stone(
                x_next,
                y_next,
                copy.deepcopy(boardUI.position_list),
                boardUI.player2.stone,
            )
            # 石の配置を画面に反映
            boardUI.update_board()

            if is_othello_end(boardUI):
                # オセロ終了時
                on_othello_end(boardUI)
                return

            if get_able_position_num(
                boardUI.position_list, boardUI.player1.stone
                ) > 0:
                # 先手が石を打つ位置がある場合
                break

            pass_num += 1

        if pass_num > 0:
            # 先手がパスした場合
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
    # 石が打てる位置
    able_position_list = []
    for x in range(ROW_NUM):
        for y in range(ROW_NUM):
            if position_list[x][y] != '':
                # 既に石がある場合
                continue
            num = 0
            for d_x, d_y in DIRECTIONS:
                # 石を打つことで反転される石の数を取得
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
    # 反転される石の数
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
        # 石を打つことで反転される石の数を取得
        num = get_turn_over_num(
            x, y, d_x, d_y, position_list, stone_put
        )
        if num > 0:
            for i in range(1, num + 1):
                position_list[x + d_x * i][y + d_y * i] = stone_put
    # 打った石
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
        # 石を打つ位置がない場合
        # x_next, y_next, evaluation
        return -1, -1, 0
    # 石が打てる位置
    able_position_list = get_able_position_list(
        position_list,
        stone_put,
    )
    # 評価値
    evaluation_list = []
    for x, y in able_position_list:
        # 石を打つ
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
            # 石を打つ位置がない場合
            # 評価値
            evaluation_list += [get_evaluation(
                position_list2,
                boardUI.player2.stone,
                )]
        else:
            depth += 1
            # 再帰的に呼び出す
            x_next, y_next, evaluation = get_next_position(
                boardUI,
                position_list2,
                STONE_OPPONENT[stone_put],
                depth,
                alpha,
                beta,
            )
            # 評価値
            evaluation_list += [evaluation]
        if stone_put == boardUI.player1.stone:
            # 先手の石を打った場合（後手の局面の場合）
            if evaluation_list[-1] < alpha:
                # αカット
                break
            if evaluation_list[-1] < beta:
                # β値を更新
                beta = evaluation_list[-1]
        else:
            # 後手（CPU）の石を打った場合（先手の局面の場合）
            if evaluation_list[-1] > beta:
                # βカット
                break
            if evaluation_list[-1] > alpha:
                # α値を更新
                alpha = evaluation_list[-1]
    # 評価値
    evaluation = 0.0
    idx = 0
    if stone_put == boardUI.player1.stone:
        # 先手の局面なら評価値が最小の手を選択
        if len(evaluation_list) > 0:
            idx = evaluation_list.index(min(evaluation_list))
    else:
        # 後手（CPU）の局面なら評価値が最大の手を選択
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
                # 自分の石の場合
                evaluation += EVALUATION_BASE[x][y]
            elif position_list[x][y] == STONE_OPPONENT[stone_put]:
                # 相手の石の場合
                evaluation -= EVALUATION_BASE[x][y]

    return evaluation


def is_othello_end(boardUI):
    # 空白数
    empty_num = 0
    # 先手の石の数
    stone_1st_num = 0
    # 後手の石の数
    stone_2nd_num = 0
    empty_num, stone_1st_num, stone_2nd_num = get_stone_num(boardUI)
    if empty_num == 0:
        return True
    elif stone_1st_num == 0:
        # 空白はあるが、全て後手の石になっている場合
        return True
    elif stone_2nd_num == 0:
        # 空白はあるが、全て先手の石になっている場合
        return True
    else:
        return False


def on_othello_end(boardUI):
    # 空白数
    empty_num = 0
    # 先手の石の数
    stone_1st_num = 0
    # 後手の石の数
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
    # 空白数
    empty_num = 0
    # 先手の石の数
    stone_1st_num = 0
    # 後手の石の数
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
