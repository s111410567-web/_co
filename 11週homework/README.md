# 第 11 週作業 — Nand2Tetris VM Translator

## 一、作業資訊

- 課程名稱：計算機結構
- 學號：111410567
- 姓名：禚鎮龍
- 作業週次：第 11 週
- 作業主題：Nand2Tetris 虛擬機器（VM Translator）
- 參考章節：第 7 章、第 8 章
- 開發語言：Python
- 開發工具：Visual Studio Code

## 二、作業目的

本次作業主要是實作 Nand2Tetris 的虛擬機器翻譯器（VM Translator），將 VM 語言指令轉換成 Hack 組合語言（Assembly）。

透過本次作業，了解堆疊運算、記憶體存取、程式流程控制及函式呼叫的運作方式。

## 三、程式功能

### 1. 堆疊運算（Stack Arithmetic）

支援以下 VM 指令：

- `add`：加法
- `sub`：減法
- `neg`：取負數
- `eq`：判斷是否相等
- `gt`：判斷是否大於
- `lt`：判斷是否小於
- `and`：AND 邏輯運算
- `or`：OR 邏輯運算
- `not`：NOT 邏輯運算

### 2. 記憶體存取（Memory Access）

支援 `push`、`pop` 指令，以及以下記憶體區段：

- constant
- local
- argument
- this
- that
- temp
- pointer
- static

### 3. 程式流程控制（Program Flow）

支援以下指令：

- `label`
- `goto`
- `if-goto`

### 4. 函式呼叫（Function Calling）

支援以下指令：

- `function`
- `call`
- `return`

並包含 Bootstrap 初始化程式的實作。

## 四、專案檔案

```text
11週homework/
├── VMTranslator.py
└── README.md
```

- `VMTranslator.py`：主要翻譯程式，負責讀取 VM 指令並產生 Hack Assembly。
- `README.md`：作業介紹、功能說明與執行方式。

## 五、執行方式

### 1. 翻譯單一 VM 檔案

在 VS Code 終端機輸入：

```powershell
python ".\_co\11週homework\VMTranslator.py" ".\_co\07\StackArithmetic\SimpleAdd\SimpleAdd.vm"
```

執行後會產生：

`SimpleAdd.asm`

### 2. 翻譯包含多個 VM 檔案的資料夾

```powershell
python ".\_co\11週homework\VMTranslator.py" ".\_co\08\FunctionCalls\FibonacciElement"
```

程式會讀取資料夾內的 VM 檔案，並輸出：

`FibonacciElement.asm`

## 六、測試項目與執行進度

### 第 7 章

| 測試項目 | 翻譯狀態 |
|---|---|
| SimpleAdd | 已產生 ASM |
| StackTest | 已產生 ASM |
| BasicTest | 已產生 ASM |
| PointerTest | 已產生 ASM |
| StaticTest | 已產生 ASM |

### 第 8 章

| 測試項目 | 翻譯狀態 |
|---|---|
| BasicLoop | 已產生 ASM |
| FibonacciSeries | 已產生 ASM |
| SimpleFunction | 已產生 ASM |
| NestedCall | 已產生 ASM |
| FibonacciElement | 已產生 ASM |
| StaticsTest | 已產生 ASM |

以上項目已透過 Python 程式產生對應的 ASM 檔案，目前尚未完成 CPU Emulator 的完整功能驗證。

## 七、學習心得

透過本次作業，我了解 VM 語言如何轉換成 Hack 組合語言，也認識了堆疊運算與記憶體存取的基本原理。

在實作過程中，使用 Python 讀取 VM 檔案，依照不同的指令產生對應的 Assembly 程式碼，並學習如何處理程式流程及函式呼叫。

這次作業讓我對虛擬機器與底層組合語言之間的關係有更進一步的認識，也能將前面章節學過的 Hack Assembly 知識應