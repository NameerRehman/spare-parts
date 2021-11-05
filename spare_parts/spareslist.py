# -*- coding: utf-8 -*-
"""
Created on Sat Jul 10 10:37:14 2021

@author: nrehman
"""
import pandas as pd
import glob, os

class SparesList():
    def __init__(self):
        self.path = input("Enter path for module files: ") #Ex: C:/Users/nrehman/Documents/Modules
        #Read all xls files in user specified folder
        self.all_modules = glob.glob(self.path + "/*")
        
        self.outputfile_name = 'd' #input('Enter name for output file: ')
        self.outputfile_path = self.path + "/" + self.outputfile_name + ".xlsx"
        
    
    def generate_list(self):
                
        #Append each file contents to dataframe
        self.bom = pd.concat((pd.read_excel(path, header=7).assign(MODULE=os.path.basename(path)) for path in self.all_modules))

        #drop all rows containing NAs in Spare Class columns
        self.bom = self.bom.dropna(subset = ['SPARE CLASS'])

        #Convert to string
        self.bom['SPARE CLASS'] = self.bom['SPARE CLASS'].astype(str)
        self.bom['MODULE'] = self.bom['MODULE'].astype(str)
        
        #Strip Spaces
        self.bom['SPARE CLASS'] = self.bom['SPARE CLASS'].str.replace(' ','')
        self.bom['MODULE'] = self.bom['MODULE'].str.replace('.xls','')
        
        #Sort df by Spare Class values
        self.bom['SPARE CLASS'] = pd.Categorical(self.bom['SPARE CLASS'], ['1','2','3','9','X'])
        self.bom = self.bom.sort_values('SPARE CLASS')
        
        #Create new df without Space Class 'X' items
        self.bom_spares = self.bom[self.bom['SPARE CLASS'] != 'X']
        
        #Create new df without duplicates
        self.bom_spares_unique = self.bom_spares.drop_duplicates(subset = ['PART NUMBER'])
        
        #Iterate through each unique part in df
        for i in range(self.bom_spares_unique.shape[0]):
            #extract part number
            part = self.bom_spares_unique['PART NUMBER'].iloc[i]
            
            #filter bom_spares by "part" & output MODULE column to a list
            #provides all module occurences of "part"
            modules_list = self.bom_spares[self.bom_spares['PART NUMBER'] == part]['MODULE'].to_list()
            
            #replace MODULE column in bom_spares_unique with modules_list
            self.bom_spares_unique['MODULE'].iloc[i] = modules_list
            
           ##TODO: GET SUM OF COLUMN INSTEAD to reduce O^n##
            
            #filter bom_spares by "part" & output PROJ QTY column to a list
            total_qty = self.bom_spares[self.bom_spares['PART NUMBER'] == part]['PROJ\nQTY.'].to_list()
            
            #Calculate sum of list
            total_qty_sum = 0
            for j in total_qty:
                try:
                    total_qty_sum+=j
                except:
                    "Couldnt add qty"
            self.bom_spares_unique['PROJ\nQTY.'].iloc[i] = total_qty_sum
        
        return self.bom, self.bom_spares, self.bom_spares_unique
        
    def export_list(self,dfs,names): 
        #Export df to excel sheet
        with pd.ExcelWriter(self.outputfile_path) as writer:
            for i in range(len(dfs)):
                dfs[i].to_excel(writer, sheet_name=names[i])
        
        print("\n Spare Parts List Created, " + self.outputfile_path)
        