# synthetic_data_generation

This repo generates synthetic data for textfields and checkboxes.
`python3 generate_random_data.py`

We need annotated template PDFs and their corresponding json schemas. 
Maintain a dir-structure like this -

TEMPLATE_PDF
  |
  |--- annotated_pdfs
  |      |--- AD2_Brokerage_to_Buyer.pdf
  |      |--- AVID_Buyer_Side.pdf
  |        
  |--- schema
  |      |--- AD2_Brokerage_to_Buyer.json
  |      |---AVID_Buyer_Side.json
  |      