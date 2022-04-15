# -*- coding: utf-8 -*-
"""
Created on Sat Jul 10 10:50:04 2021

@author: nrehman
"""

from spareslist import SparesList
from odoo import Odoo
import psycopg2
import pandas as pd

#get odoo connection data from .ini
odoo = Odoo()
login_data = odoo.loadInfo('setup.ini')

#login to odoo
odoo.authenticate(login_data['user'], login_data['password']) 

#get spare parts order history from odoo
df_orderhist, df_orderhist_tot = odoo.getOrderHistory()

#generate spare parts lists
spareslist = SparesList()
df_bom,df_bomspare,df_sparesfinal = spareslist.generate_list()

df_bom = df_bom.merge(df_orderhist_tot, on='PART NUMBER', how='left')
df_sparesfinal = df_sparesfinal.merge(df_orderhist_tot, on='PART NUMBER', how='left')


#export spares list to excel
spareslist.export_list([df_bom,df_bomspare,df_sparesfinal,df_orderhist,df_orderhist_tot],
                       ['All Parts','Spares','Spares Unique','Order History','Orders History Totals'])
