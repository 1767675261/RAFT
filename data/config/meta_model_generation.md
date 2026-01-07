You are a software requirements modeling and testing expert. I will provide two types of inputs:
1. A domain rule document;
2. Corresponding partial test cases.

Your task is to construct a **domain meta-model** for the rules of the domain. The meta-model should describe the syntax of rules in a class diagram-style tree structure. The construction of the meta-model must be completed in two steps: first, extract and confirm rule elements (15-20 leaf elements); second, based on these elements, build a three-layer meta-model and establish relationships between these elements and Precondition, Operation, and ExpectedResult.
Please strictly follow the following specifications and output format: strict, complete, and machine-readable:

### Meta-Model Construction Specifications (Must be followed)
1. **Overall Structure**
   * The meta-model should be a tree structure in class diagram style (classes and relationships only, without attributes or methods).
   * Must adopt a three-layer structure: top layer (1 node) -> middle layer (fixed 3 nodes) -> bottom layer (n leaf nodes).
   * The top-layer node is fixed as `Rule` (single class).
   * The middle layer is fixed as three classes: `Precondition`, `Operation`, `ExpectedResult`.
   * The bottom layer consists of minimal rule elements (leaf nodes).

2. **Leaf Node (Rule Element) Requirements**
   * Must be testable, quantifiable, and concrete rule elements.
   * The total number of elements must be around 15. High-frequency/core elements are listed individually; semantically overlapping elements are merged; scattered low-frequency elements are merged into a general leaf `Others`. Note: Precondition, Operation, and ExpectedResult should all include `Others`.
   * Leaf nodes should be attributes (keys), and must not include specific values or examples (e.g., "interest rate" is correct, "annual interest rate 5%" is incorrect).
   * Preferably extracted from test cases and supplemented by rule documents. Elements presented in test cases as ``RuleElement1/RuleElement2'' should be merged as a single element.
   * Elements should be reusable within the domain and cover common elements across different domain rule documents.

3. **Relationships**
   * Relationship types and applicable scenarios:
     * `contains` - composition relationship of middle-layer nodes to bottom-layer elements
     * `constrains` - constraint relationship of elements to nodes/other elements
     * `dependsOn` - prerequisite relationship of elements at runtime
     * `triggers` - operation triggering expected result
     * Other relationships
   * Every relationship must be labeled with its name in PlantUML.
   * Bottom-layer elements can only establish relationships with one of the three middle-layer nodes, and the relationship type must match the element's semantics. Carefully consider whether each rule element belongs to Precondition, Operation, or ExpectedResult.

4. **Two-Step Output Requirements**
   * **Step 1 - Rule Element List**: Output a list of approximately 15 leaf classes (class names in UpperCamelCase), each with a semantic description within 10 words.
   * **Step 2 - Meta-Model**: Construct a complete three-layer class diagram in PlantUML:
     * Top layer `Rule`;
     * Middle layer `Precondition`, `Operation`, `ExpectedResult`;
     * Bottom layer directly referencing the leaf classes from Step 1, without renaming.
   * In Step 2, clearly indicate the direction and type of all relationships, ensuring a tree hierarchy and logical consistency.

5. **Naming and Style**
   * All class names use UpperCamelCase (e.g., `AccountStatus` rather than `account_status`).
   * Class bodies remain empty (class name only).
   * Relationship names use lowercase verbs (e.g., `contains`, `triggers`).

### Output (Mandatory)
* The rule element list should be output as a numbered list; the meta-model should be output as PlantUML code.
* The number of leaf nodes must be strictly around 15; the leaf class names in Step 1 and Step 2 must match exactly (including capitalization).
* If you are unsure of which elements to include, refer to the keys in the test cases. Elements must be concise, representative, and high-frequency. For example, only one Actor should exist as a primary entity; having X Actor, Y Actor, etc., would be too repetitive.