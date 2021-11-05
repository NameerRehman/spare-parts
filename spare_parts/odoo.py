# -*- coding: utf-8 -*-
"""
Created on Sat Jul 10 10:37:51 2021

@author: nrehman
"""
import xmlrpc.client
import pandas as pd
from configparser import ConfigParser

class Odoo():
    
    def loadInfo(self,ini_filename: str):
        parser = ConfigParser()
        parser.read(ini_filename)

        # Create a dictionary of the variables stored under the "postgresql" section of the .ini
        setup_info = {param[0]: param[1] for param in parser.items("odoo")}
        
        self.common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(setup_info['url']))
        self.models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(setup_info['url']))
        self.db = setup_info['database']
        
        return setup_info

    def authenticate(self,username,password):
        self.username = username
        self.password = password
        self.uid = self.common.authenticate(self.db, self.username, self.password, {})
        print(self.uid)
        return self.uid
    
    def getPurchasePrice(self):
        purch_price = self.models.execute_kw(self.db, self.uid, self.password, 'purchase.order.line',
                        #product_type is product AND state is purchase OR release
                        #filters out service/consumables
                        'search_read', [[['product_type','=','product'],
                                         '|', ['state','=','purchase'],['state','=','release']]],
                        {'fields':['product_id','price_unit','discount','product_qty','product_uom','state','partner_id']})
        
        purch_price = pd.DataFrame(purch_price)
        return purch_price
    
    def getSalePrice(self):
        sale_price = self.models.execute_kw(self.db, self.uid, self.password, 'product.pricelist.item',
                        'search_read', [[[]]],
                        {'fields':['name']})
        
        sale_price = pd.DataFrame(sale_price)
        return sale_price
    
    
    def getProducts(self):
        sale_price = self.models.execute_kw(self.db, self.uid, self.password, 'product.product',
                        #product_type is product AND state is purchase OR release
                        #filters out service/consumables
                        'search_read', [[[]]],
                        {'fields':['product_id','engineering_code','name']}) 
        
        sale_price = pd.DataFrame(sale_price)
        return sale_price
    
    
    def getOrderHistory(self):
        order_history = self.models.execute_kw(self.db, self.uid, self.password, 'sale.order.line',
                        #product_type is product AND state is purchase OR release
                        #filters out service/consumables
                        'search_read', [[]],
                        {'fields':['name','order_partner_id','order_id','product_uom_qty','price_unit','order_id']})
        
        order_history = pd.DataFrame(order_history)
        order_history = order_history.drop(columns='id')
        
        #--------extract part number from name column
        partnum = ''
    
        for i in range(len(order_history)):
            name = order_history.iloc[i,0]
            
            #try to split at end character '_'
            try:
                split_start = name.index('[')+1 #start at after [ char
                split_end = name.index('_') #end before _ char
                partnum = name[split_start:split_end]
            except:
                pass
            
            #try to split at end character ' '
            try:
                split_start = name.index('[')+1 #start at after [ char
                split_end = name.index(' ') #end before ' ' char
                partnum = name[split_start:split_end]
            except:
                pass
                    
            partnum = partnum.replace('[','')
            partnum = partnum.replace(']','')
            order_history.iloc[i,0] = partnum
            
            #get total counts of qty sold of partnum 
            
        order_history.rename(columns={'name':'PART NUMBER','product_uom_qty':'TOTAL QTY'},inplace=True)

        order_history_tot = order_history.groupby(['PART NUMBER']).sum().reset_index()        

        return order_history, order_history_tot
    