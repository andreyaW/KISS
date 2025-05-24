from utils.helperFunctions import idx2letter

def headerFormat(workbook) -> None:
    """
    Add formatting to the headers of the worksheet.
    """
    # write the headers in the first row
    cell_format = workbook.add_format()            
    cell_format.set_bold()
    cell_format.set_text_wrap()             # wrap text to fit in cell better
    cell_format.set_border(1)               # add a thin border around the cell    
    
    return cell_format

def addTimeSteps(workbook, worksheet, i) -> None:
    """
    Add time steps to the worksheet.
    """

    # add time step headers to the first row
    if i == 0:
        time_header_format = headerFormat(workbook)  # add formatting to the headers
        time_header_format.set_right(5)              # add a thick right border to the header
        worksheet.write(0, 0, 'Time Step', time_header_format)         # add the header to the first row

    # add the time steps starting at the second row, first column
    time_col_format = workbook.add_format({'align': 'center',
                                           'right': 5})        # Add a thick right border
    worksheet.write(i+1, 0, i, time_col_format)             # data starts in the second row


def addTruth(workbook, worksheet, i, truth_data, truth_headers = None) -> None:
    """
    Add truth values to the worksheet.
    """
    # add truth headers to the first row
    if i == 0:
        for col, value in enumerate(truth_headers, start=1):
            if col == len(truth_headers):
                final_truth_header_format = headerFormat(workbook)
                final_truth_header_format.set_right(5)# Add a thick right border to last column
                worksheet.write(0, col, value, final_truth_header_format)  
            else:
                worksheet.write(0, col, value, headerFormat(workbook))

    # add the truth values starting at the second row, second column
    for col, value in enumerate(truth_data, start=1):
        if col == len(truth_data):
            final_truth_col_format = workbook.add_format({'right': 5})      # Add a thick right border to last column
            worksheet.write(i+1, col, value, final_truth_col_format)  
        else:
            worksheet.write(i+1, col, value)


def addSensed(workbook, worksheet, i, sensed_data, sensed_headers = None) -> None:
    """
    Add sensed values to the worksheet.
    """
    # add sensed headers to the first row
    if i == 0:
        for col, value in enumerate(sensed_headers,  start=len(sensed_data) + 1):
            if col == len(sensed_headers)*2:
                final_sensed_header_format = headerFormat(workbook)
                final_sensed_header_format.set_right(5)                      # Add a thick right border to last column
                worksheet.write(0, col, value, final_sensed_header_format)  
            else:
                worksheet.write(0, col, value, headerFormat(workbook))

    # add the sensed values starting at the second row, second column
    for col, value in enumerate(sensed_data, start=len(sensed_data) + 1):
        if col == len(sensed_data)*2:
            final_sensed_col_format = workbook.add_format({'right': 5})      # Add a thick right border to last column
            worksheet.write(i+1, col, value, final_sensed_col_format)  
        else:
            worksheet.write(i+1, col, value)


def addUnsensedFailureFormula(workbook, worksheet, i, truth_col, sensed_col, f1_col, num_data_points) -> None:
    if i == 0:
        # add the header for the formula column
        f1_col_header_format = headerFormat(workbook)  # add formatting to the headers
        f1_col_header_format.set_right(5)  # add a thick right border to the header
        worksheet.write(0, f1_col-1, 'Does Sensed State Match Truth State?', f1_col_header_format)
    
    row = i + 2     # formulas consider data which starts from row 2 
    truth_col = idx2letter(truth_col)  # convert column index to letter
    sensed_col = idx2letter(sensed_col)  # convert column index to letter
    f1 = f"IF({truth_col}{row} = {sensed_col}{row}, 1, 0)"
    f1_col_format = workbook.add_format({'align': 'center',
                                           'right': 5})             # Add a thick right border
    f1_col = idx2letter(f1_col)  # convert column index to letter
    worksheet.write_formula(f"{f1_col}{row}", f1, f1_col_format)    # add the formula to the cell

    # add conditional formatting to formula colums
    if i == num_data_points - 1:  # add conditional formatting after adding all the data
        # add conditional formatting to the formula column
        worksheet.conditional_format(f'{f1_col}2:{f1_col}{row}', 
                                        {'type': '2_color_scale',
                                        'min_color': '#FD0000',  # red
                                        'max_color': '#00FD00'}) # green


def addSensorFailureFormula(workbook, worksheet, i, truth_col, f2_col, num_data_points, num_objects) -> None:   
    """adds a formula sensed component worksheet to check if attached sensors are mostly working """

    if i == 0:
        # add the header for the formula column
        f2_col_header_format = headerFormat(workbook)  # add formatting to the headers
        f2_col_header_format.set_right(5)  # add a thick right border to the header
        worksheet.write(0, f2_col-1, 'Are Sensors Working?', f2_col_header_format)
    
    row = i + 2     # formulas consider data which starts from row 2 
    f2_col = idx2letter(f2_col)  # convert column index to letter
    f2_col_format = workbook.add_format({'align': 'center',
                                             'right': 5})             # Add a thick right border
    if num_objects == 1: 
        # copy sensor state from colomn C
        single_sensor_col = idx2letter(truth_col + 1)  # column index of the only sensor
        f2 = f'={single_sensor_col}{row}' # can take the first sensor state as the only sensor is present
        worksheet.write_formula(f'{f2_col}{row}', f'={single_sensor_col}{row}', f2_col_format)        
    else: 
        first_sensor_col = idx2letter(truth_col +1)
        last_sensor_col = idx2letter(truth_col + num_objects) 
        f2 = f'=MODE({first_sensor_col}{row}:{last_sensor_col}{row})' # formula to check if all sensors are working
        worksheet.write_formula(f'{f2_col}{row}', f2, f2_col_format)    # add the formula to the cell

    # add conditional formatting to formula colums
    if i == num_data_points - 1:  # add conditional formatting after adding all the data
        # add conditional formatting to the formula column
        worksheet.conditional_format(f'{f2_col}2:{f2_col}{row}', 
                                        {'type': '2_color_scale',
                                        'min_color': '#FD0000',  # red
                                        'max_color': '#00FD00'}) # green

      
def finalFormatting(worksheet, num_sub_objs) -> None:
    worksheet.freeze_panes(1, 0)           # freeze the header row

    # increase column width for better readability
    num_cols = num_sub_objs *2 + 3 + 2  # number of columns in the worksheet
    for i in range(num_cols):
        worksheet.set_column(i, i, 11.5)





def highlightParallels(workbook, worksheet, parallels, data_len, num_objects) -> None:
    ''' funtion to highlight each of the parallel sets in different colors 
        for easier readibility of simulation results '''
    
    list_of_colors = ["silver", "cyan", "yellow", "purple", "navy", "orange", "brown", "pink", "grey", "blue",]
    last_row = data_len + 2
    
    # adds the colors to the truth columns
    for i, parallel_set in enumerate(parallels):

        # get each column letter for each number in the set
        for val in parallel_set:
            col = idx2letter(val+2)

            # add conditional formatting to the worksheet
            worksheet.conditional_format(f'{col}2:{col}{last_row}',
                                        {'type': 'no_blanks',
                                         'format': workbook.add_format({'bg_color': list_of_colors[i]})})
            
    # adds the colors to the sensed columns
    for i, parallel_set in enumerate(parallels):
        # get each column letter for each number in the set
        for val in parallel_set:
            col = idx2letter(val+3+num_objects)

            # add conditional formatting to the worksheet
            worksheet.conditional_format(f'{col}2:{col}{last_row}',
                                        {'type': 'no_blanks',
                                         'format': workbook.add_format({'bg_color': list_of_colors[i]})})