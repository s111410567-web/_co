# 第八週：IC 設計 EDA 學習心得

## 題目：IC 設計的 EDA 是什麼？

### 一、EDA 的基本介紹

EDA 的全名是 Electronic Design Automation，中文稱為「電子設計自動化」，主要是利用電腦軟體協助工程師設計、模擬、測試及驗證積體電路（IC）。

由於現代晶片內部包含大量的電晶體和邏輯電路，如果全部依靠人工設計，不但需要花費很多時間，也容易發生錯誤。因此，EDA 工具可以協助工程師提高設計效率，並在晶片製造之前檢查電路是否正確。

### 二、EDA 的主要功能

EDA 的設計流程包含以下幾個重要步驟：

1. **電路設計（RTL Design）**：使用 HDL 硬體描述語言撰寫電路功能。
2. **功能模擬（Simulation）**：測試電路在不同輸入下是否產生正確結果。
3. **邏輯合成（Synthesis）**：將 HDL 程式轉換成邏輯閘組成的電路。
4. **佈局（Placement）**：安排晶片內部各個元件的位置。
5. **繞線（Routing）**：連接元件之間的訊號線路。
6. **時序分析（Timing Analysis）**：確認訊號傳遞的速度是否符合設計要求。

這些步驟可以幫助工程師確認電路不只功能正確，也能符合實際硬體的設計需求。

### 三、Veryl2Chip 軟體介紹

這次參考的 EDA 工具是 **Veryl2Chip**，它是一套可以透過瀏覽器使用的硬體設計工具，不需要另外安裝大型軟體。

Veryl2Chip 使用 Veryl 硬體描述語言，可以進行電路模擬、邏輯合成，以及 FPGA 和 ASIC 相關的設計流程。

其中的 LED 閃爍電路（Blinky）範例，是利用計數器隨著時脈增加數值，再透過計數器的位元變化控制 LED 亮滅。

這個範例讓我理解，簡單的 LED 閃爍功能，背後也需要時脈、暫存器及邏輯電路互相配合。

### 四、EDA 與計算機結構的關係

在計算機結構課程中，我們曾經使用 nand2tetris 的 HDL 撰寫 ALU、CPU、Memory 等電路元件。

當時主要是完成 HDL 程式碼，再使用測試檔確認電路功能是否正確。

透過這次了解 EDA，我發現 HDL 測試只是晶片設計流程中的一部分。真正的 IC 設計還需要進行邏輯合成、佈局、繞線及時序分析，才能逐步形成實際的硬體電路。

因此，之前課程中學習的邏輯閘、加法器、暫存器和 CPU，都可以作為理解 EDA 技術的基礎。

### 五、學習心得與結論

這次透過 Veryl2Chip 的相關資料，我對 IC 設計 EDA 有了更進一步的認識。

原本我以為電路設計主要就是撰寫 HDL 程式碼，並確認測試結果是否正確，但在了解 EDA 的完整流程後，才知道實際的晶片設計還包含許多不同的階段。

其中讓我印象比較深刻的是邏輯合成，因為工程師撰寫的 HDL 程式碼，可以透過 EDA 工具轉換成實際的邏輯閘電路，而不是像一般軟體程式一樣直接由處理器執行。

另外，我也了解到 FPGA 和 ASIC 的差異。FPGA 可以重新設定硬體功能，適合測試與開發；ASIC 則是針對特定功能設計的晶片，適合需要高效能或大量生產的應用。

我認為 EDA 最大的優點，就是可以在晶片製造之前先進行模擬與驗證，降低設計錯誤的風險，也讓複雜的電路設計更加有效率。

透過這次的學習，我也更能理解計算機結構課程中 HDL、ALU 和 CPU 的實際應用，以及它們與現代 IC 設計技術之間的關係。

### 六、參考資料

- Veryl2Chip IDE：https://ccc-eda.github.io/veryl2chip/web/dist/index.html
- Veryl2Chip GitHub：https://github.com/ccc-eda/veryl2chip
- Veryl2Chip 教學文件：https://github.com/ccc-eda/veryl2chip/blob/main/tutorial/README.tw.md
- Hack Computer HDL：https://ccc-js.github.io/hack-computer/dist/hdl.html