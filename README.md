# RAFT

RAFT is a framework for automated requirement formalization and compliance test generation. It is the official implementation for paper [Explicating Tacit Regulatory Knowledge from LLMs to Auto-Formalize Requirements for Compliance Test Case Generation](). RAFT first explicates tacit regulatory knowledge from multiple LLMs using an Adaptive Purification-Aggregation strategy and consolidates it into a domain meta-model, a formal requirement representations, and testability constraints. These artifacts are dynamically injected into prompts to guide high-precision formalization and automated test generation. Experiments on financial, automotive, and power system regulations show that RAFT achieves expert-level performance while significantly reducing generation and review effort.


![framework](framework.png)



## 1. Installation
All experiments and the following steps are conducted on Ubuntu:22.04

1. Install dependencies.

    ```bash
    sudo apt update
    sudo apt upgrade -y
    sudo apt install build-essential zlib1g-dev libbz2-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev
    sudo apt-get install -y libgl1-mesa-dev
    sudo apt-get install libglib2.0-dev
    sudo apt install wget
    sudo apt install git
    ```

2. Install miniconda.

    ```bash
    cd ~
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
    bash Miniconda3-latest-Linux-x86_64.sh
    source ~/.bashrc
    ```

3. Create a virtual python environment and install the required dependencies.
    ```bash
    git clone https://github.com/1767675261/RAFT.git
    cd RAFT
    conda create -n RAFT python=3.10
    conda activate RAFT
    pip install -r requirements.txt
    pip install -e .
    ```

4. Download necessary LLMs.

    ```bash
    git lfs install
    git clone https://huggingface.co/a1767675261/RAFT
    mkdir model
    cp -r RAFT/* model/
    rm -rf RAFT
    ```


## 2. Usage

We provide interface for Regulatory Knowledge Explication and Test Case Generation:

```
python main.py --task {TASK} --document {DOC} --testcase {TC}
```

TASK can be `meta_model_gen` for meta model generation, `requirement_representation_gen` for testable requirement representation generation, or `testcase_gen` for test case generation.

If TASK is `meta_model_gen` or `requirement_representation_gen`, DOC is the path to the regulatory document file used for RAG (e.g., `data/config/document.txt`), and TC is the path to the testcase file used for RAG (e.g., `data/config/testcase.json`). 

If TASK is `testcase_gen`, DOC is the path to the regulatory document file used for testcase generation input (e.g., `data/testcase/dataset.pdf`), and TC is the path to the testcase file used for testcase generation output (e.g., `data/testcase/testcase.json`).

**Note:** Before running the above command, please make sure to set your BASE_URL and API_KEY in the config file `data/config/api_config.json`.


## 3. Experiments

We provide scripts to reproduce the main experiments in the paper. Please refer to the `experiment/` folder for more details.

### 3.1 Experiment I: Effectiveness and Efficiency of Test Case Generation

- Datset and Experimental Results:
    - Dataset: `exp1/dataset/`
    - Ground Truth Test Cases: `exp1/testcase/`
    - Ground Truth Business Scenarios: `exp1/requirement/`
    - RAFT Results: `exp1/{llm}_ours`
    - Expert Results: `exp1/expert`
    - LLM4Fin Results: `exp1/llm4fin`
    - E2E LLMs Results: `exp1/{llm}`

- To generate test cases using RAFT, run:
    ```bash
    cd exp1
    python generate_testcase_ours.py
    ```
The results will be saved in the `exp1/{llm}_ours` folder.

- To compute metrics and draw table and figure for Experiment I, run:
    ```bash
    bash compute_prf.sh
    bash compute_rc.sh
    ```
    After the above scripts finish, run:
    ```bash
    python draw_table.py
    python draw_figure2.py
    ```
The generated table and figure will be saved in `fig/table.csv` and `fig/exp1_time.png`, respectively.

![table](/experiment/exp1/fig/table.png)

![exp1_time](/experiment/exp1/fig/exp1_time.png)

![token](/experiment/exp1/fig/token.png)


### 3.2 Experiment II: Ablation Study

#### Importance of Explicated Regulatory Knowledge

- Datset and Experimental Results:
    - Dataset: `exp2/dataset/`
    - Ground Truth Test Cases: `exp2/testcase/`
    - Ground Truth Business Scenarios: `exp2/requirement/`
    - RAFT Results: `exp2/{llm}_ours`
    - w/o Testability Knowledge Results: `exp2/{llm}_without_testability`
    - w/o Representation Knowledge Results: `exp2/{llm}_without_representation`
    - w/o All Knowledge Results: `exp2/{llm}`

- To generate test cases using RAFT with different ablations, run:
    ```bash
    cd exp2
    python generate_testcase_without_representation.py
    python generate_testcase_without_testability.py
    ```
Other results can be copyied from Experiment I.

- To compute metrics and draw figure for Experiment II, run:
    ```bash
    bash compute_prf.sh
    bash compute_rc.sh
    ```
    After the above scripts finish, run:

    ```bash
    python draw_figure.py
    ```
The generated figure will be saved in `fig/exp2_all_metrics.png`.

![exp2_all_metrics](/experiment/exp2/fig/exp2_all_metrics.png)

#### Importance of Adaptive Purification-Aggregation Strategy

- Datset and Experimental Results:
    - Dataset: `exp1/dataset/`
    - Ground Truth Test Cases: `exp1/testcase/`
    - Ground Truth Business Scenarios: `exp1/requirement/`
    - RAFT Results: `exp1/{llm}_ours`
    - w/o Adaptive Strategy Results: `exp1/{llm}_only_ours`

- To generate test cases using RAFT without adaptive strategy, follow Experiment I to generate test cases with single LLM knowledge, then run:
    ```bash
    cd exp1
    bash compute_prf_only.sh
    bash compute_rc_only.sh
    ```
    After the above scripts finish, run:
    ```bash
    python draw_figure_3.py
    ```
The generated figure will be saved in `fig/exp2_2.png`.

![exp2_2](/experiment/exp1/fig/exp2_2.png)

### 3.3 Experiment III: Generalizability Across Domains

- Datset and Experimental Results:
    - Dataset: `exp3/dataset/`
    - Ground Truth Test Cases: `exp3/testcase/`
    - Ground Truth Business Scenarios: `exp3/requirement/`
    - RAFT Results: `exp3/{llm}_ours`

- To generate test cases using RAFT in different domains, run:
    ```bash
    cd exp3
    python generate_testcase_ours.py
    ```
The results will be saved in the `exp3/{llm}_ours` folder.

- To compute metrics and draw figure for Experiment III, run:
    ```bash
    bash compute_prf.sh
    bash compute_rc.sh
    ```
    After the above scripts finish, run:
    ```bash
    python draw_figure3.py
    ```
The generated figure will be saved in `fig/exp3.png`.

![exp3](/experiment/exp3/fig/exp3.png)



---

<div align="center">

This project is licensed under the ***[MIT License](LICENSE)***.

*✨ Thanks for using **RAFT**!*

</div>