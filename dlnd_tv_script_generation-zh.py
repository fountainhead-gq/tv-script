
# coding: utf-8

# # 生成电视剧剧本
# 
# 在这个项目中，你将使用 RNN 创作你自己的[《辛普森一家》](https://zh.wikipedia.org/wiki/%E8%BE%9B%E6%99%AE%E6%A3%AE%E4%B8%80%E5%AE%B6)电视剧剧本。你将会用到《辛普森一家》第 27 季中部分剧本的[数据集](https://www.kaggle.com/wcukierski/the-simpsons-by-the-data)。你创建的神经网络将为一个在 [Moe 酒馆](https://simpsonswiki.com/wiki/Moe's_Tavern)中的场景生成一集新的剧本。
# ## 获取数据
# 我们早已为你提供了数据。你将使用原始数据集的子集，它只包括 Moe 酒馆中的场景。数据中并不包括酒馆的其他版本，比如 “Moe 的山洞”、“燃烧的 Moe 酒馆”、“Moe 叔叔的家庭大餐”等等。

# In[1]:


"""
DON'T MODIFY ANYTHING IN THIS CELL
"""
import helper

data_dir = './data/simpsons/moes_tavern_lines.txt'
text = helper.load_data(data_dir)
# Ignore notice, since we don't use it for analysing the data
text = text[81:]


# ## 探索数据
# 使用 `view_sentence_range` 来查看数据的不同部分。

# In[2]:


view_sentence_range = (0, 10)

"""
DON'T MODIFY ANYTHING IN THIS CELL
"""
import numpy as np

print('Dataset Stats')
print('Roughly the number of unique words: {}'.format(len({word: None for word in text.split()})))
scenes = text.split('\n\n')
print('Number of scenes: {}'.format(len(scenes)))
sentence_count_scene = [scene.count('\n') for scene in scenes]
print('Average number of sentences in each scene: {}'.format(np.average(sentence_count_scene)))

sentences = [sentence for scene in scenes for sentence in scene.split('\n')]
print('Number of lines: {}'.format(len(sentences)))
word_count_sentence = [len(sentence.split()) for sentence in sentences]
print('Average number of words in each line: {}'.format(np.average(word_count_sentence)))

print()
print('The sentences {} to {}:'.format(*view_sentence_range))
print('\n'.join(text.split('\n')[view_sentence_range[0]:view_sentence_range[1]]))


# ## 实现预处理函数
# 对数据集进行的第一个操作是预处理。请实现下面两个预处理函数：
# 
# - 查询表
# - 标记符号的字符串
# 
# ### 查询表
# 要创建词嵌入，你首先要将词语转换为 id。请在这个函数中创建两个字典：
# 
# - 将词语转换为 id 的字典，我们称它为 `vocab_to_int`
# - 将 id 转换为词语的字典，我们称它为 `int_to_vocab`
# 
# 请在下面的元组中返回这些字典
#  `(vocab_to_int, int_to_vocab)`

# In[3]:


import numpy as np
import problem_unittests as tests

def create_lookup_tables(text):
    """
    Create lookup tables for vocabulary
    :param text: The text of tv scripts split into words
    :return: A tuple of dicts (vocab_to_int, int_to_vocab)
    """
    # TODO: Implement Function
    vocab = sorted(set(text))
    vocab_to_int = {c: i for i, c in enumerate(vocab)}
    int_to_vocab = dict(enumerate(vocab))
    return vocab_to_int, int_to_vocab


"""
DON'T MODIFY ANYTHING IN THIS CELL THAT IS BELOW THIS LINE
"""
tests.test_create_lookup_tables(create_lookup_tables)


# ### 标记符号的字符串
# 我们会使用空格当作分隔符，来将剧本分割为词语数组。然而，句号和感叹号等符号使得神经网络难以分辨“再见”和“再见！”之间的区别。
# 
# 实现函数 `token_lookup` 来返回一个字典，这个字典用于将 “!” 等符号标记为 “||Exclamation_Mark||” 形式。为下列符号创建一个字典，其中符号为标志，值为标记。
# 
# - period ( . )
# - comma ( , )
# - quotation mark ( " )
# - semicolon ( ; )
# - exclamation mark ( ! )
# - question mark ( ? )
# - left parenthesis ( ( )
# - right parenthesis ( ) )
# - dash ( -- )
# - return ( \n )
# 
# 这个字典将用于标记符号并在其周围添加分隔符（空格）。这能将符号视作单独词汇分割开来，并使神经网络更轻松地预测下一个词汇。请确保你并没有使用容易与词汇混淆的标记。与其使用 “dash” 这样的标记，试试使用“||dash||”。

# In[4]:


def token_lookup():
    """
    Generate a dict to turn punctuation into a token.
    :return: Tokenize dictionary where the key is the punctuation and the value is the token
    """
    # TODO: Implement Function
    #from string import punctuation
    #dict_token = {c: '||'+c+'||' for i, c in enumerate(sorted(set(punctuation)))}
    dict_token = {'.': '||Period||',
                  ',': '||Comma||',
                  '"': '||Quotation_Mark||',
                  ';': '||Semicolon||',
                  '!': '||Exclamation_mark||',
                  '?': '||Question_mark||',
                  '(': '||Left_Parentheses||',
                  ')': '||Right_Parentheses||',
                  '--': '||Dash||',
                  "\n": '||Return||'}

    return dict_token

"""
DON'T MODIFY ANYTHING IN THIS CELL THAT IS BELOW THIS LINE
"""
tests.test_tokenize(token_lookup)


# ## 预处理并保存所有数据
# 运行以下代码将预处理所有数据，并将它们保存至文件。

# In[5]:


"""
DON'T MODIFY ANYTHING IN THIS CELL
"""
# Preprocess Training, Validation, and Testing Data
helper.preprocess_and_save_data(data_dir, token_lookup, create_lookup_tables)


# # 检查点
# 这是你遇到的第一个检点。如果你想要回到这个 notebook，或需要重新打开 notebook，你都可以从这里开始。预处理的数据都已经保存完毕。

# In[6]:


"""
DON'T MODIFY ANYTHING IN THIS CELL
"""
import helper
import numpy as np
import problem_unittests as tests

int_text, vocab_to_int, int_to_vocab, token_dict = helper.load_preprocess()


# ## 创建神经网络
# 你将通过实现下面的函数，来创造用于构建 RNN 的必要元素：
# 
# - get_inputs
# - get_init\_cell
# - get_embed
# - build_rnn
# - build_nn
# - get_batches
# 
# ### 检查 TensorFlow 版本并访问 GPU

# In[7]:


"""
DON'T MODIFY ANYTHING IN THIS CELL
"""
from distutils.version import LooseVersion
import warnings
import tensorflow as tf

# Check TensorFlow Version
assert LooseVersion(tf.__version__) >= LooseVersion('1.0'), 'Please use TensorFlow version 1.0 or newer'
print('TensorFlow Version: {}'.format(tf.__version__))

# Check for a GPU
if not tf.test.gpu_device_name():
    warnings.warn('No GPU found. Please use a GPU to train your neural network.')
else:
    print('Default GPU Device: {}'.format(tf.test.gpu_device_name()))


# ### 输入
# 
# 实现函数 `get_inputs()` 来为神经网络创建 TF 占位符。它将创建下列占位符：
# 
# - 使用 [TF 占位符](https://www.tensorflow.org/api_docs/python/tf/placeholder) `name` 参量输入 "input" 文本占位符。
# - Targets 占位符
# - Learning Rate 占位符
# 
# 返回下列元组中的占位符 `(Input, Targets, LearningRate)`

# In[8]:


def get_inputs():
    """
    Create TF Placeholders for input, targets, and learning rate.
    :return: Tuple (input, targets, learning rate)
    """
    # TODO: Implement Function
    inputs = tf.placeholder(tf.int32, [None, None], name='input')
    targets = tf.placeholder(tf.int32, [None, None],  name='targets')
    learningRate = tf.placeholder(tf.float32, shape=None, name='lr')
    return inputs, targets, learningRate


"""
DON'T MODIFY ANYTHING IN THIS CELL THAT IS BELOW THIS LINE
"""
tests.test_get_inputs(get_inputs)


# ### 创建 RNN Cell 并初始化
# 
# 在 [`MultiRNNCell`](https://www.tensorflow.org/api_docs/python/tf/contrib/rnn/MultiRNNCell) 中堆叠一个或多个 [`BasicLSTMCells`](https://www.tensorflow.org/api_docs/python/tf/contrib/rnn/BasicLSTMCell)
# 
# - 使用 `rnn_size` 设定 RNN 大小。
# - 使用 MultiRNNCell 的 [`zero_state()`](https://www.tensorflow.org/api_docs/python/tf/contrib/rnn/MultiRNNCell#zero_state) 函数初始化 Cell 状态
# - 使用 [`tf.identity()`](https://www.tensorflow.org/api_docs/python/tf/identity) 为初始状态应用名称 "initial_state"
#  
# 
# 返回 cell 和下列元组中的初始状态 `(Cell, InitialState)`

# In[17]:


def get_init_cell(batch_size, rnn_size):
    """
    Create an RNN Cell and initialize it.
    :param batch_size: Size of batches
    :param rnn_size: Size of RNNs
    :return: Tuple (cell, initialize state)
    """
    
    # TODO: Implement Function
    # solve the problem: BasicLSTMCell zero_state() raise error in TF1.3
    # 高于tf1.0，后续代码有问题，待解决
    # batch_size = tf.placeholder(tf.int32, [], name='batch_size')
    lstm_size = tf.contrib.rnn.BasicLSTMCell(rnn_size)
    cell = tf.contrib.rnn.MultiRNNCell([lstm_size])
    initial_state = cell.zero_state(batch_size, tf.float32)
    initial_state = tf.identity(initial_state, name='initial_state')
    return cell, initial_state



"""
DON'T MODIFY ANYTHING IN THIS CELL THAT IS BELOW THIS LINE
"""
tests.test_get_init_cell(get_init_cell)


# ### 词嵌入
# 使用 TensorFlow 将嵌入运用到 `input_data` 中。
# 返回嵌入序列。

# In[18]:


def get_embed(input_data, vocab_size, embed_dim):
    """
    Create embedding for <input_data>.
    :param input_data: TF placeholder for text input.
    :param vocab_size: Number of words in vocabulary.
    :param embed_dim: Number of embedding dimensions
    :return: Embedded input.
    """
    # TODO: Implement Function
    embedding = tf.Variable(tf.random_uniform((vocab_size, embed_dim), -1, 1))
    embed = tf.nn.embedding_lookup(embedding, input_data)
    return embed


"""
DON'T MODIFY ANYTHING IN THIS CELL THAT IS BELOW THIS LINE
"""
tests.test_get_embed(get_embed)


# ### 创建 RNN
# 你已经在 `get_init_cell()` 函数中创建了 RNN Cell。是时候使用这个 Cell 来创建 RNN了。
# 
# - 使用 [`tf.nn.dynamic_rnn()`](https://www.tensorflow.org/api_docs/python/tf/nn/dynamic_rnn) 创建 RNN
# - 使用 [`tf.identity()`](https://www.tensorflow.org/api_docs/python/tf/identity) 将名称 "final_state" 应用到最终状态中
# 
# 
# 返回下列元组中的输出和最终状态`(Outputs, FinalState)`

# In[19]:


def build_rnn(cell, inputs):
    """
    Create a RNN using a RNN Cell
    :param cell: RNN Cell
    :param inputs: Input text data
    :return: Tuple (Outputs, Final State)
    """
    # TODO: Implement Function
    outputs, final_state = tf.nn.dynamic_rnn(cell, inputs, dtype=tf.float32)
    final_state = tf.identity(final_state, name='final_state')
    return outputs, final_state


"""
DON'T MODIFY ANYTHING IN THIS CELL THAT IS BELOW THIS LINE
"""
tests.test_build_rnn(build_rnn)


# ### 构建神经网络
# 应用你在上面实现的函数，来：
# 
# - 使用你的 `get_embed(input_data, vocab_size, embed_dim)` 函数将嵌入应用到 `input_data` 中
# - 使用 `cell` 和你的 `build_rnn(cell, inputs)` 函数来创建 RNN
# - 应用一个完全联通线性激活和 `vocab_size` 的分层作为输出数量。
# 
# 返回下列元组中的 logit 和最终状态 `Logits, FinalState`

# In[20]:


def build_nn(cell, rnn_size, input_data, vocab_size, embed_dim):
    """
    Build part of the neural network
    :param cell: RNN cell
    :param rnn_size: Size of rnns
    :param input_data: Input data
    :param vocab_size: Vocabulary size
    :param embed_dim: Number of embedding dimensions
    :return: Tuple (Logits, FinalState)
    """
    # TODO: Implement Function
    embed = get_embed(input_data, vocab_size, embed_dim)
    outputs, final_state = build_rnn(cell, embed)
    logits = tf.contrib.layers.fully_connected(outputs, vocab_size, activation_fn=None)
    return logits, final_state



"""
DON'T MODIFY ANYTHING IN THIS CELL THAT IS BELOW THIS LINE
"""
tests.test_build_nn(build_nn)


# ### 批次
# 
# 实现 `get_batches` 来使用 `int_text` 创建输入与目标批次。这些批次应为 Numpy 数组，并具有形状 `(number of batches, 2, batch size, sequence length)`。每个批次包含两个元素：
# 
# - 第一个元素为**输入**的单独批次，并具有形状 `[batch size, sequence length]`
# - 第二个元素为**目标**的单独批次，并具有形状 `[batch size, sequence length]`
# 
# 如果你无法在最后一个批次中填入足够数据，请放弃这个批次。
# 
# 例如 `get_batches([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], 2, 3)` 将返回下面这个 Numpy 数组：

# In[ ]:


[
  # First Batch
  [
    # Batch of Input
    [[ 1  2  3], [ 7  8  9]],
    # Batch of targets
    [[ 2  3  4], [ 8  9 10]]
  ],
 
  # Second Batch
  [
    # Batch of Input
    [[ 4  5  6], [10 11 12]],
    # Batch of targets
    [[ 5  6  7], [11 12 13]]
  ]
]


# In[21]:


def get_batches(int_text, batch_size, seq_length):
    """
    Return batches of input and target
    :param int_text: Text with the words replaced by their ids
    :param batch_size: The size of batch
    :param seq_length: The length of sequence
    :return: Batches as a Numpy array
    """
    # TODO: Implement Function
    batches=[]
    n_batches = len(int_text) // (batch_size * seq_length)
    int_text_i = np.array(int_text[:n_batches * (batch_size * seq_length)])
    int_text_j = np.array(int_text[1:n_batches * (batch_size * seq_length) + 1])

    x_batch = np.split(int_text_i, n_batches)
    y_batch = np.split(int_text_j, n_batches)
    for i in range(n_batches):
        a = np.split(x_batch[i], batch_size)
        b = np.split(y_batch[i], batch_size)
        n_stack = np.stack((a, b), axis=0)
        batches.append(n_stack)

    return np.array(batches)


"""
DON'T MODIFY ANYTHING IN THIS CELL THAT IS BELOW THIS LINE
"""
tests.test_get_batches(get_batches)


# ## 神经网络训练
# ### 超参数
# 调整下列参数:
# 
# - 将 `num_epochs` 设置为训练次数。
# - 将 `batch_size` 设置为程序组大小。
# - 将 `rnn_size` 设置为 RNN 大小。
# - 将 `embed_dim` 设置为嵌入大小。
# - 将 `seq_length` 设置为序列长度。
# - 将 `learning_rate` 设置为学习率。
# - 将 `show_every_n_batches` 设置为神经网络应输出的程序组数量。

# In[28]:


# Number of Epochs
num_epochs = 100
# Batch Size
batch_size = 128
# RNN Size
rnn_size = 256
# Embedding Dimension Size
embed_dim = 300
# Sequence Length
seq_length = 32
# Learning Rate
learning_rate = 0.01
# Show stats for every n number of batches
show_every_n_batches = 100

"""
DON'T MODIFY ANYTHING IN THIS CELL THAT IS BELOW THIS LINE
"""
save_dir = './save'


# ### 创建图表
# 使用你实现的神经网络创建图表。

# In[29]:


"""
DON'T MODIFY ANYTHING IN THIS CELL
"""
from tensorflow.contrib import seq2seq

train_graph = tf.Graph()
with train_graph.as_default():
    vocab_size = len(int_to_vocab)
    input_text, targets, lr = get_inputs()
    input_data_shape = tf.shape(input_text)
    cell, initial_state = get_init_cell(input_data_shape[0], rnn_size)
    logits, final_state = build_nn(cell, rnn_size, input_text, vocab_size, embed_dim)

    # Probabilities for generating words
    probs = tf.nn.softmax(logits, name='probs')

    # Loss function
    cost = seq2seq.sequence_loss(
        logits,
        targets,
        tf.ones([input_data_shape[0], input_data_shape[1]]))

    # Optimizer
    optimizer = tf.train.AdamOptimizer(lr)

    # Gradient Clipping
    gradients = optimizer.compute_gradients(cost)
    capped_gradients = [(tf.clip_by_value(grad, -1., 1.), var) for grad, var in gradients if grad is not None]
    train_op = optimizer.apply_gradients(capped_gradients)


# ## 训练
# 在预处理数据中训练神经网络。如果你遇到困难，请查看这个[表格](https://discussions.udacity.com/)，看看是否有人遇到了和你一样的问题。

# In[30]:


"""
DON'T MODIFY ANYTHING IN THIS CELL
"""
batches = get_batches(int_text, batch_size, seq_length)

with tf.Session(graph=train_graph) as sess:
    sess.run(tf.global_variables_initializer())

    for epoch_i in range(num_epochs):
        state = sess.run(initial_state, {input_text: batches[0][0]})

        for batch_i, (x, y) in enumerate(batches):
            feed = {
                input_text: x,
                targets: y,
                initial_state: state,
                lr: learning_rate}
            train_loss, state, _ = sess.run([cost, final_state, train_op], feed)

            # Show every <show_every_n_batches> batches
            if (epoch_i * len(batches) + batch_i) % show_every_n_batches == 0:
                print('Epoch {:>3} Batch {:>4}/{}   train_loss = {:.3f}'.format(
                    epoch_i,
                    batch_i,
                    len(batches),
                    train_loss))

    # Save Model
    saver = tf.train.Saver()
    saver.save(sess, save_dir)
    print('Model Trained and Saved')


# ## 储存参数
# 储存 `seq_length` 和 `save_dir` 来生成新的电视剧剧本。

# In[31]:


"""
DON'T MODIFY ANYTHING IN THIS CELL
"""
# Save parameters for checkpoint
helper.save_params((seq_length, save_dir))


# # 检查点

# In[32]:


"""
DON'T MODIFY ANYTHING IN THIS CELL
"""
import tensorflow as tf
import numpy as np
import helper
import problem_unittests as tests

_, vocab_to_int, int_to_vocab, token_dict = helper.load_preprocess()
seq_length, load_dir = helper.load_params()


# ## 实现生成函数
# ### 获取 Tensors
# 使用 [`get_tensor_by_name()`](https://www.tensorflow.org/api_docs/python/tf/Graph#get_tensor_by_name)函数从 `loaded_graph` 中获取 tensor。  使用下面的名称获取 tensor：
# 
# - "input:0"
# - "initial_state:0"
# - "final_state:0"
# - "probs:0"
# 
# 返回下列元组中的 tensor `(InputTensor, InitialStateTensor, FinalStateTensor, ProbsTensor)`

# In[33]:


def get_tensors(loaded_graph):
    """
    Get input, initial state, final state, and probabilities tensor from <loaded_graph>
    :param loaded_graph: TensorFlow graph loaded from file
    :return: Tuple (InputTensor, InitialStateTensor, FinalStateTensor, ProbsTensor)
    """
    # TODO: Implement Function
    input_tensor = loaded_graph.get_tensor_by_name("input:0")
    initial_state_tensor = loaded_graph.get_tensor_by_name("initial_state:0")
    final_state_tensor = loaded_graph.get_tensor_by_name("final_state:0")
    probs_tensor = loaded_graph.get_tensor_by_name("probs:0")
    return input_tensor, initial_state_tensor, final_state_tensor, probs_tensor


"""
DON'T MODIFY ANYTHING IN THIS CELL THAT IS BELOW THIS LINE
"""
tests.test_get_tensors(get_tensors)


# ### 选择词汇
# 实现 `pick_word()` 函数来使用 `probabilities` 选择下一个词汇。

# In[34]:


def pick_word(probabilities, int_to_vocab):
    """
    Pick the next word in the generated text
    :param probabilities: Probabilites of the next word
    :param int_to_vocab: Dictionary of word ids as the keys and words as the values
    :return: String of the predicted word
    """
    # TODO: Implement Function
    pred_word = int_to_vocab[np.argmax(probabilities)]
    return pred_word


"""
DON'T MODIFY ANYTHING IN THIS CELL THAT IS BELOW THIS LINE
"""
tests.test_pick_word(pick_word)


# ## 生成电视剧剧本
# 这将为你生成一个电视剧剧本。通过设置 `gen_length` 来调整你想生成的剧本长度。

# In[35]:


gen_length = 200
# homer_simpson, moe_szyslak, or Barney_Gumble
prime_word = 'moe_szyslak'

"""
DON'T MODIFY ANYTHING IN THIS CELL THAT IS BELOW THIS LINE
"""
loaded_graph = tf.Graph()
with tf.Session(graph=loaded_graph) as sess:
    # Load saved model
    loader = tf.train.import_meta_graph(load_dir + '.meta')
    loader.restore(sess, load_dir)

    # Get Tensors from loaded model
    input_text, initial_state, final_state, probs = get_tensors(loaded_graph)

    # Sentences generation setup
    gen_sentences = [prime_word + ':']
    prev_state = sess.run(initial_state, {input_text: np.array([[1]])})

    # Generate sentences
    for n in range(gen_length):
        # Dynamic Input
        dyn_input = [[vocab_to_int[word] for word in gen_sentences[-seq_length:]]]
        dyn_seq_length = len(dyn_input[0])

        # Get Prediction
        probabilities, prev_state = sess.run(
            [probs, final_state],
            {input_text: dyn_input, initial_state: prev_state})
        
        pred_word = pick_word(probabilities[dyn_seq_length-1], int_to_vocab)

        gen_sentences.append(pred_word)
    
    # Remove tokens
    tv_script = ' '.join(gen_sentences)
    for key, token in token_dict.items():
        ending = ' ' if key in ['\n', '(', '"'] else ''
        tv_script = tv_script.replace(' ' + token.lower(), key)
    tv_script = tv_script.replace('\n ', '\n')
    tv_script = tv_script.replace('( ', '(')
        
    print(tv_script)


# # 这个电视剧剧本是无意义的
# 如果这个电视剧剧本毫无意义，那也没有关系。我们的训练文本不到一兆字节。为了获得更好的结果，你需要使用更小的词汇范围或是更多数据。幸运的是，我们的确拥有更多数据！在本项目开始之初我们也曾提过，这是[另一个数据集](https://www.kaggle.com/wcukierski/the-simpsons-by-the-data)的子集。我们并没有让你基于所有数据进行训练，因为这将耗费大量时间。然而，你可以随意使用这些数据训练你的神经网络。当然，是在完成本项目之后。
# # 提交项目
# 在提交项目时，请确保你在保存 notebook 前运行了所有的单元格代码。请将 notebook 文件保存为 "dlnd_tv_script_generation.ipynb"，并将它作为 HTML 文件保存在 "File" -> "Download as" 中。请将 "helper.py" 和 "problem_unittests.py" 文件一并提交。
