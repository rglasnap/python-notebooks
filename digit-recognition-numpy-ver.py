# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.9.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# + _cell_guid="b1076dfc-b9ad-4769-8c92-a6c4dae69d19" _uuid="8f2839f25d086af736a60e9eeb907d3b93b6e0e5"
# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load in 

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
from scipy import optimize
from sklearn.metrics import mean_absolute_error, f1_score
from matplotlib import pyplot as plt
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split

# Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

sample_submission = pd.read_csv("../input/digit-recognizer/sample_submission.csv")
test = pd.read_csv("../input/digit-recognizer/test.csv")
train = pd.read_csv("../input/digit-recognizer/train.csv")

# Any results you write to the current directory are saved as output.

# + [markdown] _cell_guid="79c7e3d0-c299-4dcb-8224-4455121ee9b0" _uuid="d629ff2d2480ee46fbb7e2d37f6b5fab8052498a"
# Next up is based on some code I'd written previously in MATLAB. While ultimately this is recreating neural network code that other libraries already implement, I'm doing this as an exercise in using numpy. 

# +
def sigmoid(z):
    return 1 / (1 + np.exp(-z))

def sigmoidGradient(z):
    """Caclulate the gradient of the sigmoid function"""
    return sigmoid(z) * (1 - sigmoid(z))

def normalize(X):
    (m, n) = X.shape
    
    # This is so we don't get divide by zero errors.
    # TODO: Take this out and run the data through PCA to see if that helps.
    epsilon = 1e-100
    
    # Noramlizing each pixel/feature column
    mu = np.mean(X, axis=0).reshape(1,n)
    X_norm = X - mu
    sigma = np.std(X_norm, axis=0, ddof=1).reshape(1,n)
    
    return X_norm/(sigma+epsilon)
    


# +
def NNCostFunction(nn_params, input_layer_sz, hidden_layer_sz, num_labels, X, y, my_lambda=0 ):
    """Calculate the cost function and associated gradients for a two-layer Neural Network where each 
    neuron uses the sigmoid function. 
    
    Arguments:
        Theta1: First set of NN parameter weightings
        Theta2: Second set of NN parameter weightings
        input_layer_sz_sz: Size of the input layer
        hidden_layer_sz: Size of the hidden layer
        num_labels: Number of output neurons
        X: Array of data
        y: Array of output
        my_lambda: Regularization parameter
        
    Return Values:
        J: Cost function
        grad: Gradient of the Cost function
    """
    
    # Initial setup of useful variables and return values.
    (m, n) = X.shape
    J = 0
    
    Theta1 = nn_params[:hidden_layer_sz*(input_layer_sz+1)].reshape(hidden_layer_sz,input_layer_sz+1)
    Theta2 = nn_params[hidden_layer_sz*(input_layer_sz+1):].reshape(num_labels,hidden_layer_sz+1)
    
    # Add bias element
    X = np.insert(X, 0, 1, axis=1)
    
    # Calculate the hidden layer
    a2 = sigmoid(X @ Theta1.T)
    
    # Add the bias elements
    a2 = np.insert(a2, 0, 1, axis=1)
    
    # Calculate the output layer.
    h = sigmoid(a2 @ Theta2.T)
    
    # Convert y to a matrix with rows as each example (still), and columns corresponding to each output neuron. 
    y = y.reshape(m,1) == np.arange(10)
    
    # Calculate the cost
    # Testing out two different ways of doing this first looping through columns
    J = np.sum(1/m * ( -(y*np.log(h)) - (1-y) * np.log(1-h)))
    #for k in range(y.shape[1]):
    #    J = J + 1/m * (-(y[:,k] @ np.log(h[:,k])) - (1-y[:,k]) @ np.log(1-h[:,k]))
    
    # Regularization goes here
    #TODO: Convert Regularization from MatLab code
    return(J)
    
def NNGradFunction(nn_params, input_layer_sz, hidden_layer_sz, num_labels, X, y, my_lambda=0 ):
    
    # Initial setup of useful variables and return values.
    (m, n) = X.shape
    
    Theta1 = nn_params[:hidden_layer_sz*(input_layer_sz+1)].reshape(hidden_layer_sz,input_layer_sz+1)
    Theta2 = nn_params[hidden_layer_sz*(input_layer_sz+1):].reshape(num_labels,hidden_layer_sz+1)
    
    Theta1_grad = np.zeros(Theta1.shape)
    Theta2_grad = np.zeros(Theta2.shape)
    
    # Inert bias element (1) into X before index 0
    X = np.insert(X, 0, 1, axis=1)
    # Convert y to a matrix with rows as each example (still), and columns corresponding to each output neuron. 
    y = y.reshape(m,1) == np.arange(10)
    
    # Backpropagation
    # TODO: Test different types of loops to see which is faster
    #for t in range(m)
    #for (a,b) in zip(Xmod,ymod): print(a.shape,b.shape):   
    for t in range(m):
        
        #Feeding things through first.
        a_1 = X[t,:]
        
        # Hidden layer feed through.
        # Bias elements already added earlier, no need to add them now
        z_2 = a_1 @ Theta1.T
        a_2 = sigmoid(z_2)
        
        # Output layer feed through
        # Add bias elements first.
        a_2 = np.insert(a_2, 0, 1)
        z_3 = a_2 @ Theta2.T
        a_3 = sigmoid(z_3)
        
        # Backpropagation
        
        d_3 = a_3 - y[t,:]
        
        d_2 = (d_3 @ Theta2 ) * np.insert(sigmoidGradient(z_2), 0, 0)
        
        # Ditch the bias unit column
        d_2 = np.delete(d_2, 0)
        
        # Accumulate gradients
        # Adding some dimensions to convert these into true row vectors
        d_2 = np.expand_dims(d_2,axis=0)
        d_3 = np.expand_dims(d_3,axis=0)
        a_1 = np.expand_dims(a_1,axis=0)
        a_2 = np.expand_dims(a_2,axis=0)
        
        Theta1_grad = Theta1_grad + d_2.T @ a_1
        Theta2_grad = Theta2_grad + d_3.T @ a_2
    
    # Average out all of the values
    # TODO: Add Regularization term
    Theta1_grad = Theta1_grad/m
    Theta2_grad = Theta2_grad/m
    
    grad = np.concatenate( (Theta1_grad.flatten(),Theta2_grad.flatten()) )

    return(grad)


# +
def predict(Theta1, Theta2, X):
    h1 = sigmoid( np.insert(X, 0, 1, axis=1) @ Theta1.T)
    h2 = sigmoid( np.insert(h1, 0, 1, axis=1) @ Theta2.T)
    return np.argmax(h2,axis=1)

def mycallback(result):
    global NFeval
    print("Iteration Number: ", str(NFeval))
    NFeval+=1

# +
# Main Code Setup
# Initially limtiting this to the first 5 entries for testing purposes.


X = train.loc[:, train.columns != 'label'].to_numpy()
y = train.loc[:, 'label'].to_numpy()

# TODO: Do this with a standardization pipeline. Which will probably fix the div0 issues too. 
X_norm = normalize(X)

# Code section for PCA
# The following is based on Interactive Intro to Dimensionality Reduction on Kaggle. 

# Caclulate the covariant matrix first.

X_cov = np.cov(X_norm.T)

evals, evecs = np.linalg.eig(X_cov)


eig_pairs = [ ( np.abs(evals[i]), evecs[i]) for i in range(len(evals)) ]

eig_pairs.sort(key = lambda x: x[0], reverse = True)

eval_tot = sum(evals)

indvdl_contribs = [(i/eval_tot) for i in sorted(evals, reverse=True)]
overal_contribsz = np.cumsum(indvdl_contribs)

# We want to find out where the eigenvectors contribute over 90% of our variance. 
np.argmax(overal_contribs > 0.90)
# -

# Just for fun let's take a look at it
plt.plot(np.arange(len(evals)), overal_contribs )

# +
# Now for some actual PCA
# Using 228 components

pca = PCA(n_components=228)
pca.fit(X_norm)
X_new = pca.transform(X_norm)


# +
# Now that we've normalized and reduced the data split it into a validation and training set.

X_train, X_val, y_train, y_val = train_test_split(X_norm, y)


# Various useful constants
(m, n) = X_train.shape
input_layer_sz = n
hidden_layer_sz = 25
num_labels = 10
batch_sz = 500
alphas = np.array([0.3, 1, 3, 10])
alpha=0.1
iterations=5

Theta1 = np.random.rand(hidden_layer_sz, input_layer_sz + 1)*0.12*2 - 0.12
Theta2 = np.random.rand(num_labels, hidden_layer_sz + 1)*0.12*2 - 0.12

init_params = np.concatenate((Theta1.flatten(),Theta2.flatten()))

# Heavy lifting code section

#[J , nn_params] = NNCostFunction(params, input_layer_sz, hidden_layer_sz, num_labels, X_norm, y)

#fmin = optimize.minimize(fun=NNCostFunction, x0=params, args=(input_layer_sz, hidden_layer_sz, num_labels, X_norm, y), method='CG',
#                            jac=NNGradFunction, tol=mytol, options={'disp': True, 'maxiter':50, 'gtol':mytol }, callback=mycallback)


for alpha in alphas:
    params = np.copy(init_params)

    Jhist = np.zeros(iterations)

    # TODO: Do some of this with args and kwargs.
    for iters in range(iterations):
        # Using a factor of 0.1 as a base starting point
        for i in range(0,m,batch_sz):
            grad = NNGradFunction(params, input_layer_sz, hidden_layer_sz, num_labels, X_train[i:i+batch_sz], y_train[i:i+batch_sz])

            params = params - alpha*grad
            J = NNCostFunction(params, input_layer_sz, hidden_layer_sz, num_labels, X_train[i:i+batch_sz], y_train[i:i+batch_sz])

            print("\rIteration: {} Batch Start: {}  Cost: {}".format(iters,i,J), end='', flush=True)
        Jhist[iters] = J

    Theta1 = params[:hidden_layer_sz*(input_layer_sz+1)].reshape(hidden_layer_sz,input_layer_sz+1)
    Theta2 = params[hidden_layer_sz*(input_layer_sz+1):].reshape(num_labels,hidden_layer_sz+1)


    val_predictions = predict(Theta1, Theta2, X_val)
    fscore = f1_score(y_val,val_predictions,average='micro')

    plt.figure()
    plt.plot(np.arange(iterations),Jhist)
    plt.title("Alpha: {} F1 Score: {}".format(alpha, fscore))
    plt.xlabel("Iterations")
    plt.ylabel("Cost")
    plt.legend(['Training','Validation'])
    plt.show()

# -




# +
mytol = 1e-3
NFeval = 1

fmin = optimize.minimize(fun=NNCostFunction, x0=params, args=(input_layer_sz, hidden_layer_sz, num_labels, X_new, y), method='CG',
                            jac=NNGradFunction, tol=mytol, options={'disp': True, 'maxiter':50, 'gtol':mytol }, callback=mycallback)

# +
fTheta1 = fmin.x[:hidden_layer_sz*(input_layer_sz+1)].reshape(hidden_layer_sz,input_layer_sz+1)
fTheta2 = fmin.x[hidden_layer_sz*(input_layer_sz+1):].reshape(num_labels,hidden_layer_sz+1)

fmin_predictions = predict(fTheta1, fTheta2, X_new)

f1_score(y,fmin_predictions,average='micro')


# +
#Actual predictions here

X_test = test.loc[:, test.columns != 'label'].to_numpy()
X_test_norm = normalize(X_test)

test_predictions = predict(fTheta1, fTheta2, X_test_norm)

output = pd.DataFrame({'ImageId': test.index+1,
                       'Label': test_predictions})
output.to_csv('submission.csv', index=False)
# -


