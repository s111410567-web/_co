
# 第十週：Hack Assembler 組譯器

## 一、作業目標

本週作業為 nand2tetris 第 6 章，
使用 Python 實作 Hack Assembler（組譯器）。

主要功能是將 Hack 組合語言（.asm）
轉換成 16 位元二進位機器碼（.hack）。

## 二、程式功能

1. 讀取 .asm 組合語言檔案
2. 移除空白與註解
3. 轉換 A 指令（@value）
4. 轉換 C 指令（dest=comp;jump）
5. 處理標籤（Label）
6. 自動分配變數記憶體位址
7. 輸出 .hack 機器碼檔案

## 三、程式檔案

| 檔案名稱 | 說明 |
|---|---|
| Assembler.py | Hack 組譯器主程式 |
| Add.asm | 加法測試程式 |
| Add.hack | 執行組譯器後產生的機器碼 |

## 四、執行方式

在 VS Code 終端機輸入：

```bash
python week10/Assembler.py week10/Add.asm
```

程式會讀取 Add.asm，
並在相同資料夾產生 Add.hack。

## 五、程式設計原理

本程式使用兩輪組譯方式：

第一輪：讀取組合語言並記錄標籤位置。

第二輪：處理變數及指令轉換，
將 A 指令與 C 指令翻譯成機器碼。

## 六、學習心得

透過本次作業，我了解到組合語言與機器碼之間的關係。

Assembler 的工作是將人類比較容易閱讀的組合語言，
轉換成電腦能夠執行的二進位指令。

這次使用 Python 實作組譯器，
讓我更加了解 Hack 電腦的指令格式、
符號表及程式翻譯的基本流程。

## 七、參考資料

- https://www.nand2tetris.org/project06
