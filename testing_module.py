try:
    from ebay_delivery_prediction_project import Preprocessing
    Preprocessing.import_test()
    print("Test Successful.")
except Exception as e:
    print("Something went wrong.")
    print("Error : \n", e)