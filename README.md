# Ebay delivery prediction

# Data
## Manually Download
I didn't implement an automated tool for downloading data since only us 3 will be using this codebase.
For data to be properly downloaded the 2 given files 'train.tsv' and 'quiz.tsv' should be in "./data/supplied_data".

Link to the dataset : https://drive.google.com/file/d/1ex7TlDCuna5YH2A06GPcSjTVzbk51--k/view?usp=sharing

# Other Data
If we ever get additional data then I'll put it in a google drive link which will be using the exact samem file structure.
For example, the contents of the "data" folder in the drive should be inserted into the "/data" folder in your local repo clone.

# Installing
The source code is in "./ebay_delivery_prediction_project" to install it as a package please run "pip install -e ." from the project root directory.
This will make it possible to import any of the functions in the notebooks.

# Updating the source code
If you change any of the source code in the please run "pip install -e ." from the root directory again. 
After updating any code, jupyter-notebooks need to be restarted, simply reimporting won't work.
You can then test the function from the notebooks.
 
When updating the source code ensure that all functions are backwards compatible so that nothing breaks.

When adding any classes/modules/python files to the source code, add them to "./ebay_delivery_prediction_project/\_\_init__.py" to ensure that they are importable in the module.

# Pushing Code
When pushing any update, push them in a separate branch and issue a merge request so I can review it before we add the changes to the main branch. (I also need to figure out how to do this)-Swagget

# Testing Installation
To see if the module is correctly installed please run "python testing_module.py" from the root. The output should be "Test Successful."