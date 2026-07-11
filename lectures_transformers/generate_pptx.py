import os
import sys

# Ensure python-pptx is available or install it
try:
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.enum.text import PP_ALIGN
    from pptx.dml.color import RGBColor
    from pptx.enum.shapes import MSO_SHAPE
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-pptx"])
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.enum.text import PP_ALIGN
    from pptx.dml.color import RGBColor
    from pptx.enum.shapes import MSO_SHAPE

# Color Palette inspired by 3Blue1Brown
DARK_BLUE = RGBColor(10, 25, 47)       # Primary dark color
MID_BLUE = RGBColor(28, 73, 110)       # Secondary theme color
LIGHT_CYAN = RGBColor(116, 192, 227)   # Accent color (data/embeddings)
BROWN_WEIGHT = RGBColor(140, 98, 57)   # Accent color (weights)
BG_LIGHT = RGBColor(248, 249, 250)     # Slide background
TEXT_DARK = RGBColor(40, 40, 40)       # Body text color
WHITE = RGBColor(255, 255, 255)
HIGHLIGHT_RED = RGBColor(220, 53, 69)

def set_slide_background(slide, color):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color

def create_textbox(slide, left, top, width, height):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0)
    tf.margin_right = Inches(0)
    tf.margin_top = Inches(0)
    tf.margin_bottom = Inches(0)
    return tf

def add_title(slide, text, subtitle_text=None, dark=False):
    tf = create_textbox(slide, Inches(0.75), Inches(0.5), Inches(11.83), Inches(1.2))
    p = tf.paragraphs[0]
    p.text = text
    p.font.name = 'Georgia'
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = WHITE if dark else DARK_BLUE
    
    if subtitle_text:
        p2 = tf.add_paragraph()
        p2.text = subtitle_text
        p2.font.name = 'Calibri'
        p2.font.size = Pt(18)
        p2.font.color.rgb = LIGHT_CYAN if dark else MID_BLUE

def add_bullet_points(tf, points, bullet_level=0):
    for i, pt in enumerate(points):
        if i == 0 and tf.paragraphs[0].text == "":
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = pt[0]
        p.level = bullet_level + pt[1]
        p.font.name = 'Calibri'
        p.font.size = Pt(20 - (pt[1] * 2))
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(8)

def add_callout(slide, left, top, width, height, text, bg_color=MID_BLUE, text_color=WHITE):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.color.rgb = bg_color
    tf = shape.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.alignment = PP_ALIGN.CENTER
    p.font.name = 'Calibri'
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = text_color
    return shape

def add_title_slide(prs, title, subtitle):
    slide = prs.slides.add_slide(prs.slide_layouts[6]) # blank layout
    set_slide_background(slide, DARK_BLUE)
    
    tf = create_textbox(slide, Inches(1.0), Inches(2.2), Inches(11.33), Inches(3.0))
    p = tf.paragraphs[0]
    p.text = title
    p.alignment = PP_ALIGN.CENTER
    p.font.name = 'Georgia'
    p.font.size = Pt(44)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.space_after = Pt(20)
    
    p2 = tf.add_paragraph()
    p2.text = subtitle
    p2.alignment = PP_ALIGN.CENTER
    p2.font.name = 'Calibri'
    p2.font.size = Pt(24)
    p2.font.color.rgb = LIGHT_CYAN
    
    p3 = tf.add_paragraph()
    p3.text = "Based on 3Blue1Brown Lessons"
    p3.alignment = PP_ALIGN.CENTER
    p3.font.name = 'Calibri'
    p3.font.size = Pt(14)
    p3.font.color.rgb = WHITE
    p3.space_before = Pt(40)
    
    return slide

def add_standard_slide(prs, title, points, callout_text=None, layout_type="left_points_right_callout"):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, BG_LIGHT)
    add_title(slide, title)
    
    if layout_type == "left_points_right_callout" and callout_text:
        # Bullet points on the left
        tf = create_textbox(slide, Inches(0.75), Inches(1.8), Inches(6.5), Inches(4.8))
        add_bullet_points(tf, points)
        
        # Callout box on the right
        add_callout(slide, Inches(7.8), Inches(2.2), Inches(4.5), Inches(3.5), callout_text)
    elif layout_type == "full_points":
        tf = create_textbox(slide, Inches(0.75), Inches(1.8), Inches(11.83), Inches(4.8))
        add_bullet_points(tf, points)
    
    return slide

# ==========================================
# LECTURE 1 GENERATION
# ==========================================
def build_lecture_1():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    
    # Slide 1: Title
    add_title_slide(prs, "Lecture 1: Large Language Models\n& The Transformer Architecture", "A Visual and High-Level Introduction")
    
    # Slide 2: What is a GPT Model?
    add_standard_slide(prs, "What is a GPT Model?", [
        ("Generative Pre-trained Transformer", 0),
        ("A neural network architecture optimized for processing sequence data like text, audio, and images.", 1),
        ("Generative: Produces new text based on input instructions.", 0),
        ("Pre-trained: Learns grammar, facts, and reasoning from reading massive web-scale datasets.", 0),
        ("Transformer: The core model structure, introduced by Google researchers in 2017.", 0),
    ], "Generative: Produces text\nPre-trained: Reads the web\nTransformer: The network")
    
    # Slide 3: The Fundamental Task
    add_standard_slide(prs, "The Core Objective: Next-Token Prediction", [
        ("LLMs generate content by solving a simple repeating puzzle:", 0),
        ("\"Given a prompt, predict the single most likely word/token that comes next.\"", 1),
        ("Autoregressive Generation Cycle:", 0),
        ("1. Take in prompt.", 1),
        ("2. Calculate probability distribution over all possible words.", 1),
        ("3. Sample one word (semi-randomly based on probability).", 1),
        ("4. Append word to prompt, and repeat the cycle.", 1),
        ("This step-by-step loop is why chat applications stream text word-by-word.", 0)
    ], "Prompt\n↓\nPredict next word\n↓\nSample word\n↓\nAppend & Repeat")
    
    # Slide 4: Tokenization
    add_standard_slide(prs, "Tokenization: Slicing Text for Computers", [
        ("Computers process numbers, not letters. Raw text must be broken down:", 0),
        ("Tokens: Small chunks of characters (whole words, parts of words, punctuation).", 0),
        ("Example sentence splits:", 0),
        ("\"To date, the cleverest thinker of all time was...\"", 1),
        ("→ [To] [ date] [,] [ the] [ cle] [ve] [rest] [ thinker] [ of] [ all] [ time] [ was]", 2),
        ("Vocabulary Map: Each unique token is mapped to an ID integer.", 0),
        ("GPT-3 uses a vocabulary of ~50,257 unique tokens.", 1)
    ], "Raw Text\n↓\nTokenization\n↓\nToken IDs (Integers)\n↓\nModel Input")
    
    # Slide 5: The Three Core Blocks
    add_standard_slide(prs, "The Core Steps inside the Transformer", [
        ("1. Input Embeddings", 0),
        ("Transforms token ID integers into coordinate vectors in a high-dimensional space.", 1),
        ("2. Attention Block", 0),
        ("Allows tokens to 'talk' to one another to absorb context and update vectors.", 1),
        ("3. MLP (Feed-Forward) Block", 0),
        ("Processes each token's vector individually and in parallel, asking attribute questions.", 1),
        ("By alternating Attention and MLP blocks, the model extracts deep semantics.", 0)
    ], "Embeddings (Represent)\n↓\nAttention (Communicate)\n↓\nMLP (Analyze)\n↓\nPrediction (Output)")
    
    # Slide 6: Input Embeddings
    add_standard_slide(prs, "Input Embeddings: Geometric Meaning", [
        ("Each token ID is mapped to a vector v in a massive space.", 0),
        ("Dimensions represent abstract semantic concepts (learned automatically).", 0),
        ("Geometric features:", 0),
        ("Similar meanings group together in the coordinate space.", 1),
        ("Directions represent semantic adjustments (e.g. past tense, pluralization, gender).", 1),
        ("Embeddings lay the foundation of representation for the network.", 0)
    ], "High-Dimensional Vector Space\n(e.g., 12,288 dimensions for GPT-3)\n\nDirections = Concepts\nClustering = Similarity")
    
    # Slide 7: Attention Block
    add_standard_slide(prs, "The Attention Block: Adding Context", [
        ("Static embeddings do not account for context. Attention fixes this.", 0),
        ("Example: The word \"model\"", 0),
        ("\"A machine learning model\" vs \"A famous fashion model\"", 1),
        ("The attention mechanism lets \"model\" communicate with neighbors:", 0),
        ("It identifies which words are relevant to contextualizing the vector.", 1),
        ("It updates coordinates accordingly so the vector represents its exact context.", 1),
    ], "Static Word Embedding\n+\nContextual Communications\n=\nContext-Rich Embedding")
    
    # Slide 8: MLP Block
    add_standard_slide(prs, "The MLP Block: Parallel Processing", [
        ("Following communication, vectors are passed through a Multilayer Perceptron.", 0),
        ("No Cross-Talk: Tokens do not communicate with each other in this block.", 0),
        ("Parallel Execution: The same operations are performed on all vectors simultaneously.", 0),
        ("Conceptual Operation:", 0),
        ("Acts as a database lookup. It asks questions about each vector's attributes:", 1),
        ("\"Is this word part of a science fiction context?\"", 2),
        ("\"Is this verb conjugated in the past tense?\"", 2),
        ("Updates the vector's position based on the answers.", 1)
    ], "MLP (Feed-Forward)\n\nProcesses tokens independently\n\nActs like a rich\nfeature-updating database")
    
    # Slide 9: Layer Stacking
    add_standard_slide(prs, "Deep Learning: Stacking Layers", [
        ("A single block of Attention + MLP is not enough for complex reasoning.", 0),
        ("Deep Stacks:", 0),
        ("GPT-2 Small has 12 repeating layers.", 1),
        ("GPT-3 has 96 layers.", 1),
        ("Information Progression:", 0),
        ("Early Layers: Extract basic grammar, syntax, and sentence structure.", 1),
        ("Middle Layers: Track coreferences and clause connections.", 1),
        ("Late Layers: Formulate high-level semantic answers to predict the next word.", 1)
    ], "Stacked Layers\n\n[Layer 96] ← High Semantic\n...\n[Layer 2]  ← Context refinement\n[Layer 1]  ← Syntactic features\n[Embeds]   ← Raw Words")
    
    # Slide 10: Deep Learning Premise
    add_standard_slide(prs, "Deep Learning Premise: Weights vs. Data", [
        ("When running an LLM, we separate the parameters from the active state:", 0),
        ("The Weights (The Brains):", 0),
        ("Tunable parameters configured during training.", 1),
        ("Stored as static matrices (e.g. 175 billion weights for GPT-3).", 1),
        ("The Data (The Flow):", 0),
        ("Intermediate vectors representing current text.", 1),
        ("constantly modified as they stream through the network layers.", 1)
    ], "Weights (Matrices):\nLearned and static.\n\nData (Tensors/Vectors):\nDynamic user input.")
    
    # Slide 11: Summary
    add_standard_slide(prs, "Summary: Lecture 1 Key Takeaways", [
        ("GPT models predict the next token in a loop to write text.", 0),
        ("Text is tokenized and projected as high-dimensional embedding vectors.", 0),
        ("Attention allows vectors to query and adjust based on context.", 0),
        ("MLP layers process each token vector independently to check attributes.", 0),
        ("Deep stacking allows networks to build complex semantic representations.", 0)
    ], "Lecture 1 Completed!\n\nUp Next: Math of Embeddings & the Residual Stream")
    
    prs.save("lecture1.pptx")
    print("Saved lecture1.pptx")

# ==========================================
# LECTURE 2 GENERATION
# ==========================================
def build_lecture_2():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    
    # Slide 1: Title
    add_title_slide(prs, "Lecture 2: Inside the Transformer", "Embeddings, The Residual Stream, and Softmax Math")
    
    # Slide 2: Word Embeddings & Vector Dimensions
    add_standard_slide(prs, "Word Embeddings & Dimensions", [
        ("Tokens are mapped to vectors v in a high-dimensional vector space.", 0),
        ("Model Dimensions (d):", 0),
        ("GPT-2 Small: d = 768 dimensions", 1),
        ("GPT-3: d = 12,288 dimensions", 1),
        ("Coordinates encode linguistic features:", 0),
        ("Directions correspond to concepts (e.g., gender, tense, capitalization).", 1),
        ("A single vector represents the combination of all these attributes.", 1),
        ("Represented as: v = [0.12, -0.45, 0.89, ... 12,288 values]", 0)
    ], "GPT-3 Vector Space\n\nd = 12,288 dimensions\n\nEach position in the array is a coordinate along an axis of meaning.")
    
    # Slide 3: Semantic Geometry
    add_standard_slide(prs, "Semantic Geometry & Vector Math", [
        ("Because dimensions represent concepts, we can do semantic math:", 0),
        ("Semantic Equation Examples:", 0),
        ("v_King - v_Man + v_Woman ≈ v_Queen", 1),
        ("v_Italy - v_Rome + v_Paris ≈ v_France", 1),
        ("Measuring Similarity:", 0),
        ("We calculate Cosine Similarity between vectors to test semantic closeness:", 1),
        ("Cosine Similarity = (a · b) / (||a|| ||b||)", 2),
        ("Aligned vectors have a dot product near 1; perpendicular vectors have 0.", 1)
    ], "Semantic Math:\n\nKing - Man + Woman\n= Queen\n\nRome - Italy + France\n= Paris")
    
    # Slide 4: Positional Encoding
    add_standard_slide(prs, "Positional Encoding: Injecting Order", [
        ("Transformers process tokens in parallel, making them order-blind (bag of words).", 0),
        ("To represent sequence structure:", 0),
        ("We add a position vector p_j to the word embedding e_j at index j:", 1),
        ("x_j = e_j + p_j", 2),
        ("The positional vector encodes the word's position in the prompt.", 1),
        ("Sinusoidal Encodings:", 0),
        ("Values are calculated using sine and cosine waves of varying frequencies.", 1),
        ("Enables the model to determine relative distances between words easily.", 1)
    ], "e_j (Semantic Vector)\n+\np_j (Position Vector)\n=\nx_j (Input Vector)")
    
    # Slide 5: The Residual Stream
    add_standard_slide(prs, "The Residual Stream: The Central Highway", [
        ("How does information propagate through dozens of stacked layers?", 0),
        ("The Residual Stream is the central channel where vectors travel.", 0),
        ("Key Architecture Pattern:", 0),
        ("Instead of rewriting the token vector completely, blocks only add shifts (Δv):", 1),
        ("v_out = v_in + Δv", 2),
        ("Benefits:", 0),
        ("1. Identity Highway: Information can travel untouched across the network.", 1),
        ("2. Stable Backpropagation: Prevents vanishing gradients during training.", 1),
        ("3. Incremental updates: Layers act as modifiers rather than rebuilders.", 1)
    ], "Residual Stream\n\n=== [Identity Path] ===\n  ▲           │\n  │ (Add Δv)  ▼ (Read)\n[ Attention / MLP ]")
    
    # Slide 6: Layer Stacking Mechanics
    add_standard_slide(prs, "Layer Stacking: A Complete Block Step", [
        ("Let's look at the mathematical loop of a single transformer layer:", 0),
        ("First Step: Multi-Head Attention", 0),
        ("The attention block reads from the stream, computes updates, and writes:", 1),
        ("v' = v + Attention(v)", 2),
        ("Second Step: Multilayer Perceptron (MLP)", 0),
        ("The MLP reads the updated vector, computes adjustments, and writes:", 1),
        ("v'' = v' + MLP(v')", 2),
        ("This process repeats. The residual stream is constantly read and updated.", 0)
    ], "v\n↓\n[Attention] → v + Attn(v)\n↓\n[MLP] → v' + MLP(v')\n↓\nv'' (Next Layer)")
    
    # Slide 7: The Softmax Function
    add_standard_slide(prs, "Softmax Function: Output Probabilities", [
        ("At the very end of the network, we must output word predictions.", 0),
        ("The final token vector is multiplied by the unembedding matrix to get raw scores (logits) x for each word in the vocabulary.", 0),
        ("Softmax converts logits x into valid probabilities P(i):", 0),
        ("P(i) = e^(x_i) / Σ_j e^(x_j)", 1),
        ("Key Math features:", 0),
        ("Exponentiation: Makes all negative raw scores positive.", 1),
        ("Summation: Divides each by the sum of all, so probabilities total 1.0 (100%).", 1),
        ("Amplification: The largest score is dramatically boosted, while minor differences shrink.", 1)
    ], "Logits (Raw Scores)\n[-2.4, 1.2, 5.8, ...]\n\n↓ [Softmax]\n\nProbabilities\n[0.01, 0.04, 0.95, ...]")
    
    # Slide 8: Softmax Temperature
    add_standard_slide(prs, "Softmax Temperature: Adjusting randomness", [
        ("We can scale the logits by a temperature parameter T before Softmax:", 0),
        ("P(i) = e^(x_i / T) / Σ_j e^(x_j / T)", 1),
        ("Low Temperature (T < 1.0, e.g., T = 0.2):", 0),
        ("Accentuates the differences. The highest score gets close to 100% probability.", 1),
        ("Result: High confidence, repetitive, factual, and predictable text.", 2),
        ("High Temperature (T > 1.0, e.g., T = 1.5):", 0),
        ("Flattens the probability peaks. Lower scores get higher chances.", 1),
        ("Result: Diverse, random, creative, but prone to grammatical mistakes/hallucinations.", 2)
    ], "Logits / T\n\nLow T (T=0.2) → Greedy/Predictable\n\nHigh T (T=1.5) → Random/Creative")
    
    # Slide 9: GPT-3 Parameter Breakdown
    add_standard_slide(prs, "Parameter Breakdown (Where do 175B weights go?)", [
        ("GPT-3 has 175 Billion parameters across 96 layers. Where are they?", 0),
        ("Embedding Matrix:", 0),
        ("50,257 tokens × 12,288 dimensions ≈ 617 Million parameters.", 1),
        ("Attention Layers (per layer):", 0),
        ("Queries, Keys, Values (Q, K, V) projection matrices + Output Matrix.", 1),
        ("≈ 600 Million parameters per layer × 96 layers ≈ 58 Billion parameters.", 2),
        ("MLP Layers (per layer):", 0),
        ("Two large projection matrices mapping vectors to 4× size (49,152) and back.", 1),
        ("≈ 1.2 Billion parameters per layer × 96 layers ≈ 115 Billion parameters.", 2)
    ], "Total Parameters:\n\nMLP Blocks: ~65%\nAttention Blocks: ~33%\nEmbeddings: ~2%")
    
    # Slide 10: Summary
    add_standard_slide(prs, "Summary: Lecture 2 Key Takeaways", [
        ("Tokens are mapped to coordinate vectors in a high-dimensional space.", 0),
        ("Semantic calculations (e.g. analogy math) are possible in this space.", 0),
        ("Positional encoding ensures sequence order is tracked.", 0),
        ("The **Residual Stream** enables stable depth by updating vectors via addition (v + Δv).", 0),
        ("**Softmax** converts logits to probabilities, and **Temperature** scales output entropy.", 0)
    ], "Lecture 2 Completed!\n\nUp Next: Attention Details (Q, K, V math)")
    
    prs.save("lecture2.pptx")
    print("Saved lecture2.pptx")

# ==========================================
# LECTURE 3 GENERATION
# ==========================================
def build_lecture_3():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    
    # Slide 1: Title
    add_title_slide(prs, "Lecture 3: The Attention Mechanism", "Queries, Keys, Values, and Multi-Head Math")
    
    # Slide 2: Motivation: Context and Ambiguity
    add_standard_slide(prs, "Why Attention? Resolving Polysemy", [
        ("A word's meaning is highly dependent on its context.", 0),
        ("Consider the ambiguous word \"mole\":", 0),
        ("\"American shrew mole\" (Animal context).", 1),
        ("\"One mole of carbon dioxide\" (Chemistry context).", 1),
        ("\"Take a biopsy of the mole\" (Medical context).", 1),
        ("Goal of Attention:", 0),
        ("To enable vectors of words like \"mole\" to query their surroundings and absorb coordinates from contextual keywords like \"shrew\", \"biopsy\", or \"carbon\".", 1)
    ], "Ambiguous Word\n\"mole\"\n\nContext Clues\n\"shrew\", \"biopsy\"\n\nUpdated Embedding\nRefined coordinates")
    
    # Slide 3: Information Transfer
    add_standard_slide(prs, "Information Transfer: Vector Shifts", [
        ("How does information transfer between tokens?", 0),
        ("We want the vector for the target word (\"mole\") to shift its coordinates.", 0),
        ("To achieve this:", 0),
        ("We calculate an attention connection between tokens.", 1),
        ("We compute an update vector Δv from context tokens (e.g. \"American\", \"shrew\") and add it directly to \"mole\".", 1),
        ("This mathematically embeds the contextual concept of \"animal\" into the representation of the word \"mole\".", 1)
    ], "American  ──┐\n             ├─→ [mole]\nshrew     ──┘\n\nVectors add up to update target token coordinates.")
    
    # Slide 4: Queries, Keys, and Values
    add_standard_slide(prs, "Queries, Keys, and Values (Q, K, V)", [
        ("For each token representation x_i, we project it into three distinct roles:", 0),
        ("Query (q_i): \"What am I looking for in context?\"", 0),
        ("q_i = W_Q x_i", 1),
        ("Key (k_j): \"What information do I contain or offer?\"", 0),
        ("k_j = W_K x_j", 1),
        ("Value (v_j): \"What content do I transfer to matching tokens?\"", 0),
        ("v_j = W_V x_j", 1),
        ("W_Q, W_K, and W_V are learned parameter matrices.", 0)
    ], "Query (Q): What I want\nKey (K): What I have\nValue (V): What I give")
    
    # Slide 5: Step 1: Attention Scores
    add_standard_slide(prs, "Step 1: Calculating Match Scores", [
        ("We measure the alignment of Query i and Key j using the dot product:", 0),
        ("Raw Score_ij = q_i · k_j = q_i^T k_j", 1),
        ("If what token i is searching for matches what token j offers, the score is high.", 1),
        ("Scaling by Key Dimension:", 0),
        ("We divide raw scores by the square root of the key dimension (√d_k):", 1),
        ("Scaled Score_ij = (q_i^T k_j) / √d_k", 2),
        ("Why? High-dimensional dot products have high variance. Without scaling, Softmax outputs values close to 0 or 1, freezing gradients (vanishing gradient problem).", 1)
    ], "Scaled Score:\n\nq_i^T k_j\n────────\n  √d_k\n\nKeeps gradients healthy during backprop.")
    
    # Slide 6: Causal Masking
    add_standard_slide(prs, "Causal Masking: Restricting the Future", [
        ("In autoregressive text generation, tokens cannot see future words.", 0),
        ("To enforce this restriction:", 0),
        ("Before Softmax, we apply a mask to the score matrix.", 1),
        ("All scores where j > i (future tokens) are set to -∞.", 1),
        ("Masked Score_ij = Raw Score_ij (for j ≤ i) or -∞ (for j > i).", 1),
        ("Since e^(-∞) = 0, future tokens receive exactly 0 attention weighting.", 0),
        ("Ensures sequence generation remains causal and realistic.", 0)
    ], "Causal Mask Matrix:\n\n[ s11  -∞  -∞ ]\n[ s21  s22 -∞ ]\n[ s31  s32 s33]\n\nFuture tokens are completely blanked out.")
    
    # Slide 7: Step 2: Softmax & Update Vector
    add_standard_slide(prs, "Step 2: Normalization & Weighted Sum", [
        ("We run the masked, scaled scores through Softmax to get weights A_ij:", 0),
        ("A_ij = e^(Score_ij) / Σ_k e^(Score_ik)", 1),
        ("These weights act as percentage indicators (summing to 1.0 or 100%).", 1),
        ("Calculating the Update Vector (u_i):", 0),
        ("We compute a weighted sum of the Value vectors using the weights A_ij:", 1),
        ("u_i = Σ_j A_ij v_j", 2),
        ("u_i contains the synthesized contextual information retrieved from all permitted context tokens.", 0)
    ], "Attention Weights (A_ij)\n[0.1, 0.7, 0.2, 0.0]\n\n×\n\nValue Vectors (v_j)\n\n=\nUpdate Vector (u_i)")
    
    # Slide 8: The Output Projection
    add_standard_slide(prs, "Step 3: Writing to the Residual Stream", [
        ("The update vector u_i must be mapped back to the residual stream space.", 0),
        ("Output Matrix multiplication:", 0),
        ("We multiply u_i by the Output Projection matrix W_O:", 1),
        ("Δx_i = W_O u_i", 2),
        ("This maps the retrieved value back into the original embedding dimension d.", 1),
        ("Residual Stream update:", 0),
        ("x_next = x_prev + Δx_i", 1),
        ("The token vector is updated with context while preserving its original identity.", 0)
    ], "u_i (Update Vector)\n↓\n[ W_O Matrix ]\n↓\nΔx_i (Projected Update)\n↓\nResidual Stream (x + Δx)")
    
    # Slide 9: Multi-Head Attention
    add_standard_slide(prs, "Multi-Head Attention: Parallel Focus", [
        ("A single attention process (a head) can only track one query concept at a time.", 0),
        ("To extract multiple contextual relationships in parallel:", 0),
        ("We instantiate multiple attention heads (e.g. 96 heads in GPT-3).", 1),
        ("Each head runs its own independent Q, K, and V operations:", 1),
        ("Head 1: Tracks noun-adjective associations.", 2),
        ("Head 2: Tracks pronouns and their corresponding subjects.", 2),
        ("Head 3: Tracks verbs and their direct objects.", 2),
        ("Outputs of all heads are concatenated and projected together via W_O.", 0)
    ], "Parallel Attention:\n\n[Head 1] → Nouns\n[Head 2] → Pronouns\n[Head 3] → Verbs\n\nCombined and written to stream via W_O.")
    
    # Slide 10: Parameter Counting
    add_standard_slide(prs, "Attention Block Parameter Counts", [
        ("Let's calculate the weights in a single attention layer of GPT-3:", 0),
        ("Layer Dimensions: d = 12,288. Heads = 96. Head dimension = 128.", 1),
        ("Q, K, V Projection Matrices:", 0),
        ("For each head: W_Q, W_K, W_V are each 12,288 × 128 in size.", 1),
        ("Weights per head = 3 × (12,288 × 128) ≈ 4.7 Million parameters.", 1),
        ("For all 96 heads = 96 × 4.7M ≈ 452 Million parameters.", 1),
        ("Output Projection Matrix (W_O):", 0),
        ("W_O size is 12,288 × 12,288 ≈ 151 Million parameters.", 1),
        ("Total per Attention block ≈ 603 Million parameters per layer!", 0)
    ], "Attention Block (per layer):\n\nQ, K, V Projections:\n~452M parameters\n\nOutput Projection (W_O):\n~151M parameters\n\nTotal: ~603M parameters")
    
    # Slide 11: Summary
    add_standard_slide(prs, "Summary: Lecture 3 Key Takeaways", [
        ("Attention allows vectors to dynamically absorb surrounding context.", 0),
        ("Queries, Keys, and Values represent what tokens seek, offer, and transfer.", 0),
        ("Matching is measured via dot products, scaled to preserve gradients, and masked to prevent looking ahead.", 0),
        ("Weighted value vectors are mapped back to the residual stream via W_O.", 0),
        ("Multi-head attention tracks distinct textual relationships simultaneously.", 0)
    ], "Lecture 3 Completed!\n\nAll three presentations are ready.")
    
    prs.save("lecture3.pptx")
    print("Saved lecture3.pptx")

if __name__ == "__main__":
    build_lecture_1()
    build_lecture_2()
    build_lecture_3()
