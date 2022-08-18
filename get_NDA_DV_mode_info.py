# -*- coding: utf-8 -*-
"""
* Web scraping and optimization of https://cneos.jpl.nasa.gov/nda/nda.html , deltaV mode
* Minimum dv to deflect asteroid, given a direction of the dv and required periapse distance
* Things can get messy depending on the internet connection and number of instances
* Users may fiddle with the time-based parameters to decrease chances of nans or unrun cases
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from numpy import sign 
from numpy.random import uniform



def initiate_website():
    
    time_buffer = 5
    wait_for_browser = 5
    wait_for_website = 10
    wait_for_dropdown = 2.5
    
    time.sleep(uniform(time_buffer/2,time_buffer,1)[0])
    driver = webdriver.Firefox()
    time.sleep(wait_for_browser)
    driver.get("https://cneos.jpl.nasa.gov/nda/nda.html")
    time.sleep(wait_for_website)
    driver.switch_to.frame("nda")   
    
    select = Select(driver.find_element(By.ID,'object'))

    select.select_by_visible_text('PDC23 a=0.99 i=10 e=0.09')
    time.sleep(wait_for_dropdown)

    return driver

def get_NDA_DV_mode_info(session, input_list):
    
    wait_for_next_iteration = 2.5
    
    wait_for_next_entry = 0.2
    
    time.sleep(wait_for_next_iteration)
    
    
    input_names =["td", "deltava", "deltavc", "deltavn"]
    
    for count, input_name in enumerate(input_names): 
        element=session.find_element(By.ID,input_name)
        element.send_keys(Keys.BACK_SPACE)
        element.send_keys(Keys.BACK_SPACE)
        element.send_keys(Keys.BACK_SPACE)
        element.send_keys(Keys.BACK_SPACE)
        element.send_keys(Keys.BACK_SPACE)
        element.send_keys(Keys.BACK_SPACE)
        element.send_keys(Keys.BACK_SPACE)        
        element.send_keys( str( input_list[count] ) )
        element.send_keys(Keys.ENTER)
        time.sleep(wait_for_next_entry)    
    
        output_list_names = ["deltavaout", "deltavcout", "deltavnout", "totaldeltav", 
                             "orbitalperiodbefore", "orbitalperioddelta", "bdotzeta", 
                             "bmagnitude", "captureradius", "closeapproachradius",
                             "missdistance", "vinfinity"]
    
        output_list = []
        
        
        for output in output_list_names:      
            result=session.find_element(By.ID, output)
            output_list.append( result.text)
             
      
    return output_list


def run_NDA_DV_mode(deflection_time, desired_distance, direction):

    try:
        session = initiate_website()
        
        dva = 100
                
        i = 0
        
        
        direction = direction
        
        dva = sign(direction) * dva
        
        while i < 10:
        
            input_list = [deflection_time,dva,0,0]
            output_list = get_NDA_DV_mode_info(session, input_list)  
            peri_dist =  float(output_list[9])
            
            dva1 = dva - 1
            input_list1 = [deflection_time,dva1,0,0]
            output_list1 = get_NDA_DV_mode_info(session, input_list1) 
            peri_dist1 =  float(output_list1[9])
                  
            
            dperi_dist = (peri_dist - peri_dist1)/(dva - dva1)
            
            # stop
            alpha = 1
            
            new_dva = round(dva - alpha * (peri_dist-desired_distance)/dperi_dist, 3)  
            
            if(direction>=0 ):  # posigrade
                if(new_dva<0):
                    new_dva = round(dva + alpha * peri_dist/dperi_dist, 3)
                
            else: #retrograde
                if(new_dva>0):
                    new_dva = round(dva + alpha * peri_dist/dperi_dist, 3)
        
            
            
            new_peri_dist = round(float(get_NDA_DV_mode_info(session, [deflection_time,new_dva,0,0])[9]), 3)
        
        
            error = 100*abs(new_peri_dist - desired_distance) / desired_distance
            
            if error <= 1: 
                break    
            
    
            dva = new_dva
                
        
            i = i+1
                    
        session.quit()            
                    
        
        file = open('timedeflection_'+str(deflection_time)+'_days_direction'+str(direction)+'_distance'+str(new_peri_dist)+'_Re.csv', 'w+')   
        
        file.writelines('Deflection time[days], dva [mm/s], Periapse distance [Re], Direction ' + '\n')   
        file.writelines(str(deflection_time) + ' ' + str(new_dva)+ ' ' + str(new_peri_dist)+ ' ' + str(direction) +'\n')    
    
                    
        file.close()           

    except:  
        pass              
    
    return None
                
                
            