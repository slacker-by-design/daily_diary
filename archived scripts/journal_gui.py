from dateutil.relativedelta import relativedelta
from datetime import datetime
import calendar as cal
import tkinter as tk
from tkinter import ttk
from journal_backend import JournalData, Day, Month

class JournalApp():
    def __init__(self, root):
        self.window = root
        self.start()
    
    #calling the startup functions
    def start(self):
        self.journal_data = JournalData()
        self.initial_date_vars()
        self.size_vars()
        self.window_attributes()
        self.ttk_styles()
        self.get_backend_objs()
        self.build_selection_frame()
        self.build_journal_frame()
        self.build_calendar_selection_frame()
        self.select_journal()
        
    #setting the current date variables
    def initial_date_vars(self):
        #Setting the current date
        today = datetime.today()
        self.current_date =today.date()
        
        #tkinter variables
        self.selection_label_var = tk.StringVar()  

    #size touples (x,y)
    def size_vars(self):
        self.window_size = (600,800)
        self.selection_frame_size = (self.window_size[0],75)
        self.journal_frame_size = (self.window_size[0], self.window_size[1]-self.selection_frame_size[1])
        self.daily_options_frame_size = (self.window_size[0], 150)
        self.journal_entry_frame_size = (self.window_size[0], self.journal_frame_size[1]-self.daily_options_frame_size[1])

    #initializing the styles used
    def ttk_styles(self): 
        style = ttk.Style()
        style.theme_use('alt')
        style.configure('TFrame', borderwidth = 2, relief = 'sunken')
        style.configure('ActiveGoal.TButton', background = 'green')
        style.configure('InactiveGoal.TButton', background = 'grey')

    #building tables and getting the month object
    def get_backend_objs(self):
        #make sure the tables are built and getting the appropriate month object
        with JournalData() as journal_data:
            journal_data.create_tables()
            self.month = Month(self.current_date.month,self.current_date.year,journal_data)

        #set the initial day variable
        self.entry_text = ' '
        self.select_day() 

    #shaping and labeling the main window
    def window_attributes(self):
        self.window.geometry(f'{self.window_size[0]}x{self.window_size[1]}+250+100')
        self.window.resizable(False, False)
        self.window.title('Journal and Goals')

    #build out the top selection frame (select between journal or calendar)
    def build_selection_frame(self):
        #build out the needed widgets
        self.selection_frame = ttk.Frame(self.window)
        #buttons and date/month label (will swap from date to month depending on what frame is visible)
        self.journal_button = ttk.Button(self.selection_frame, text = 'Journal', command = self.select_journal)
        self.selection_frame_lable = ttk.Label(self.selection_frame, textvariable=self.selection_label_var)
        self.calendar_button = ttk.Button(self.selection_frame, text = 'Calendar', command = self.select_calendar)

        #place the built widgets
        self.journal_button.place(anchor = 'w', relx = .1, rely = .5, width = 75, height = 40)
        self.selection_frame_lable.place(anchor = 'center', relx = .5, rely = .5, width = 150, height = 40)
        self.calendar_button.place(anchor = 'e', relx = .9, rely=.5, width = 75, height = 40)
        self.selection_frame.place(x = 0, y = 0, relwidth=1, height = self.selection_frame_size[1])
 
    #change the label in the selection frame between the date and month depending on what section you are in (journal or calendar)
    def change_selection_frame_label(self, how):
        if how == 'date':
            date = self.current_date.strftime('%B %d, %Y')
            self.selection_label_var.set(date)
        elif how == 'month':
            month = self.current_date.strftime('%B')
            self.selection_label_var.set(month)

    #center journal frame
    def build_journal_frame(self):
        #build the frames and widgets for the main window
        self.journal_frame = ttk.Frame(self.window)
        self.journal_entry_frame = ttk.Frame(self.journal_frame)
        self.journal_entry = tk.Text(self.journal_entry_frame)
        
        #build the lower part of the window that will hold the goal buttons and edit buttons
        self.build_daily_options_frame()        

        #place the built widgets
        self.journal_entry.place(x = 3, y =3, relwidth=.99, relheight=.99)
        self.journal_entry_frame.place(x = 0, y = 0, relwidth=1, height = self.journal_entry_frame_size[1])
        self.journal_frame.place(x = 0, y = self.selection_frame_size[1], relwidth=1, height = self.journal_frame_size[1])

        #set the text in the journal entry to the given days entry
        self.set_entry_text()

    #building out the bottom frame with the gaols to select and the save day and edit goals button
    def build_daily_options_frame(self):
        #build needed frame and widgets
        self.daily_options_frame = ttk.Frame(self.journal_frame)
         #these buttons will be placed and removed with the selection buttons
        self.edit_goals_button = ttk.Button(self.daily_options_frame, text = 'Edit Goals', command = self.build_edit_goals_main_frame)
        self.save_day_button = ttk.Button(self.daily_options_frame, text = 'Save Day', command=self.save_day_data)

        #populating the daily goal button dictionary to keep track and assign configure each goal button
        self.daily_goal_button_dict = self.populate_goal_buttons(self.daily_options_frame,(4,4),(0,0))
        
        #makes the goal buttons togglable and sets them to the appropriate states for the given day
        self.make_goal_buttons_toggle()
        self.set_init_goal_button_states()

        #place the frame, the other widgets will be placed in other functions
        self.daily_options_frame.place(x = 0, y = self.journal_entry_frame_size[1], relwidth=1, height = self.daily_options_frame_size[1])

        #sets weights for the frames grid rows and columns
        for i in range(4):
            self.daily_options_frame.grid_columnconfigure(i, weight = 1, uniform = 'daily_options_columns')
        
        for i in range(4):
            self.daily_options_frame.grid_rowconfigure(i, weight = 1, uniform = 'daily_options_uniform_rows')

    #create all the goal buttons as well as the goal button dictionary 
    #'frame' is where the buttons will be placed, 'size' is a touple of (colums, rows), 'where' is a touple of where to start (column, row)
    def populate_goal_buttons(self, frame, size, where):
        #getting the goals dictionary from the journal data
        with JournalData() as journal_data:
            goals_dict = journal_data.get_goals_dict()

        #holds the button objects to be called on later
        goal_button_dict = {}
        num_columns, num_rows = size
        column, row = where

        #build and grid the buttons using the goals dictionary as a reference
        for i, id in enumerate(goals_dict):
            goal_button = ttk.Button(frame, text = goals_dict[id])
            goal_button.grid(column = column, row = row)
            goal_button_dict[id] = goal_button

            row = row if column <num_columns -1 else row +1
            column = column +1 if column <num_columns-1 else 0
        
        #returns the new goal button dictionary for the given frame
        return goal_button_dict
    
    #give each goal id a 'state' of it's button, then config the button command to call the toggle function
    def make_goal_buttons_toggle(self):
        for id in self.daily_goal_button_dict:
            button_state = tk.BooleanVar(value = 0)
            goal_button = self.daily_goal_button_dict[id]
            goal_button.config(command = lambda b = id, s = button_state: self.toggle_goal_button(b,s))
            self.daily_goal_button_dict[id] = [goal_button, button_state]

    #toggle the active/inactive style of each button
    def toggle_goal_button(self, button_id, state):
        button_state = state.get()
        button =self.daily_goal_button_dict[button_id][0]
        if button_state == 0:
            self.daily_goal_button_dict[button_id][1] = 1
            button.config(style = 'ActiveGoal.TButton')
        else:
            self.daily_goal_button_dict[button_id][1] = 0
            button.config(style = 'InactiveGoal.TButton')
        
    #build frame and children to select goals to edit or add goals
    def build_edit_goals_main_frame(self):
        #build needed frame and widgets
        self.edit_goals_frame = ttk.Frame(self.window)
        self.edit_goals_label = ttk.Label(self.edit_goals_frame, text = 'Click on a goal to edit/delete')
        self.add_goal_button = ttk.Button(self.edit_goals_frame, text = 'Add Goal', command = self.build_add_goal_frame)
        self.close_button = ttk.Button(self.edit_goals_frame, text = 'Done', command = self.rebuild_daily_options_frame)

        #build out the goal buttons
        self.edit_goal_dict = self.populate_goal_buttons(self.edit_goals_frame, (2,5),(0,1))

        #set the command to open edit individual goal options
        for id in self.edit_goal_dict:
            self.edit_goal_dict[id].configure(command = lambda id=id: self.build_edit_indv_goal_frame(id))
           
        #place and grid the widgets
        self.edit_goals_label.grid(column = 0, row = 0, columnspan=2, sticky='nsew')
        self.add_goal_button.grid(column = 0, row = 6)
        self.close_button.grid(column = 1, row = 6)
        self.edit_goals_frame.place(anchor = 'center', relx=.5, rely=.5, height = 250, width = 300)

        #assign the grid columns and rows the same weight and make them uniform, keepint them the same size
        for i in range(2):
            self.edit_goals_frame.grid_columnconfigure(i, weight = 1, uniform = 'edit_goals_columns')

        for i in range(7):
            self.edit_goals_frame.grid_rowconfigure(i, weight = 1, uniform = 'edit_goals_rows')

    #rebuild the daily options frame to show the updated goals
    def rebuild_daily_options_frame(self):
        self.edit_goals_frame.destroy()
        self.build_daily_options_frame()
        self.edit_goals_button.grid(column = 0, row = 3)
        self.save_day_button.grid(column = 3, row = 3)

    #small frame and children to add an actual goal
    def build_add_goal_frame(self):
        self.add_goal_frame = ttk.Frame(self.edit_goals_frame)
        entry_label = ttk.Label(self.add_goal_frame, text = 'Enter goal:')
        self.goal_entry = ttk.Entry(self.add_goal_frame)
        add_button = ttk.Button(self.add_goal_frame, text = 'Add Goal', command = self.add_goal)

        self.add_goal_frame.place(anchor = 'center', relx = .5, rely = .5, height = 150, width = 150)
        entry_label.pack()
        self.goal_entry.pack()
        add_button.pack()

    #adds goal to the journal data
    def add_goal(self):
        goal = [self.goal_entry.get()]
        with JournalData() as journal_data:
            journal_data.add_goals(goal)
        
        self.edit_goals_frame.destroy()
        self.build_edit_goals_main_frame()

    #build the edit an individual goal frame
    def build_edit_indv_goal_frame(self, id):
        #get the goal description from the button that was pressed given the id
        goal = self.edit_goal_dict[id].cget('text')
        
        #build out the frame and needed widgets
        self.edit_indv_goal_frame = ttk.Frame(self.edit_goals_frame)
        edit_label = ttk.Label(self.edit_indv_goal_frame, text = 'Change or Delete Goal')
        self.edit_indv_goal_entry = ttk.Entry(self.edit_indv_goal_frame)
        delete_button = ttk.Button(self.edit_indv_goal_frame, text = 'Delete Goal', command = lambda: self.delete_indv_goal(id))
        update_button = ttk.Button(self.edit_indv_goal_frame, text = 'Update Goal', command = lambda: self.edit_indv_goal(id))
        cancel_button = ttk.Button(self.edit_indv_goal_frame, text = 'Cancel', command = self.edit_indv_goal_frame.destroy)

        #fill in the entry with the goal to be edited
        self.edit_indv_goal_entry.insert(0, goal)

        #place frame and widgets
        self.edit_indv_goal_frame.place(anchor= 'center', relx = .5, rely = .5, height = 150, width = 225)
        edit_label.place(relx = .05, rely=0, relheight=.25, relwidth=.9)
        self.edit_indv_goal_entry.place(relx = .05, rely = .25, relheight = .25, relwidth=.9)
        delete_button.place(anchor = 'ne',relx = .45, rely = .5, relheight=.25, relwidth=.4)
        update_button.place(anchor = 'nw', relx = .55, rely = .5, relheight=.25, relwidth=.4)
        cancel_button.place(relx = .3, rely = .75, relheight=.25, relwidth=.4)

    #edit individual goal function, sends goal id and new description to journal backend
    def edit_indv_goal(self,id):
        edited_goal = self.edit_indv_goal_entry.get()
        with JournalData() as journal_data:
            journal_data.edit_goal(id,edited_goal)
        self.edit_goals_frame.destroy()
        self.build_edit_goals_main_frame()

    #delete individual goal function, sends goal id to journal backend
    def delete_indv_goal(self, id):
        with JournalData() as journal_data:
            journal_data.delete_goal(id)
        self.edit_goals_frame.destroy()
        self.build_edit_goals_main_frame()

    #build the selected calendar frame
    def build_calendar_selection_frame(self):
        #build widgets
        self.calendar_section_frame = ttk.Frame(self.window)       
        self.prev_month_button = ttk.Button(self.calendar_section_frame, text = 'Prev')
        self.next_month_button = ttk.Button(self.calendar_section_frame, text = 'Next')
        self.calendar_frame = ttk.Frame(self.calendar_section_frame)
        
        #build calendar buttons and place them
        self.cal_day_button_matrix = self.build_calendar_day_matrix()

        #place widgets in frame
        self.calendar_section_frame.place(x = 0, y = self.selection_frame_size[1], relwidth=1, height = self.journal_entry_frame_size[1])
        self.calendar_frame.place(anchor = 'center', relx = .5, rely = .5, height = 300, width = 300)
        self.prev_month_button.place(anchor = 'ne', relx = .45, y = 5, height= 35, width = 75)
        self.next_month_button.place(anchor = 'nw', relx = .55, y = 5, height = 35, width = 75)

    #stores a 7x6 matrix of buttons and their visible states. if they are visible, the state will be True
    def build_calendar_day_matrix(self):
        for i in range(6):
            self.calendar_frame.grid_rowconfigure(i, weight = 1, uniform = 'calendar_rows')
        for i in range(7):
            self.calendar_frame.grid_columnconfigure(i, weight = 1, uniform = 'calendar_columns')
        cal_day_button_maxtrix = []
        for row in range(6):
            button_list = []
            for column in range(7):
                day_button = ttk.Button(self.calendar_frame)
                day_state = False
                button_list.append([day_button,day_state,(column,row)])
            cal_day_button_maxtrix.append(button_list)
        return cal_day_button_maxtrix
    
    #reveal calendar based on what day objects are in the day matrix
    def reveal_cal_days(self):
        day_matrix = self.month.day_matrix

        for i, week in enumerate(self.cal_day_button_matrix):
            
            for d,button in enumerate(week):
                day = day_matrix[i][d]
                column, row = button[2] #touple of the column, row
                if day == None and button[1] == True:
                    button[0].grid_forget()
                    button[1] = False
                elif day:
                    button[0].grid(column = column, row = row, sticky = 'nsew')
                    button[0].configure(text = day.date.day)
                    button[0].configure(command = lambda date = day.date: self.set_current_date(date))

    #select journal section, from journal button in selection frame
    def select_journal(self):
        self.journal_frame.tkraise()
        self.change_selection_frame_label('date')
        self.edit_goals_button.grid(column = 0, row = 3)
        self.save_day_button.grid(column = 3, row = 3)
        
    #select calendar section, from calendar button in selection frame
    def select_calendar(self):
        self.calendar_section_frame.tkraise()
        self.change_selection_frame_label('month')
        self.reveal_cal_days()
        self.edit_goals_button.grid_forget()
        self.save_day_button.grid_forget()

    #changes the current date, then updates the needed data and widgets
    def set_current_date(self,date):
        self.current_date = date
        self.select_day()
        self.set_entry_text()
        self.select_journal()
        self.set_init_goal_button_states()
        
    #selects and sets the current day object using the current day variable
    def select_day(self):
        self.day = self.month.get_day(self.current_date)
        self.entry_text = self.day.entry
        
    #set goal button states
    def set_init_goal_button_states(self):
        goal_dict = self.day.goals #goals as dictionary with key = id, values = [goal description, completion state]
        
        for id in self.daily_goal_button_dict:    
            #checks to make sure there actually is the given goal for the given day
            if id in goal_dict:
                state = goal_dict[id][1]
                #sets state and style for the goal button
                if state == 1:
                    self.daily_goal_button_dict[id][1] = state 
                    self.daily_goal_button_dict[id][0].config(style = 'ActiveGoal.TButton')
                elif state == 0:
                    self.daily_goal_button_dict[id][1] = state
                    self.daily_goal_button_dict[id][0].config(style = 'InactiveGoal.TButton')
            else:
                self.daily_goal_button_dict[id][0].config(style = 'InactiveGoal.TButton')
     
    # set the journal entry text to the already saved text, if there is any
    def set_entry_text(self):
        if type(self.entry_text) == tuple:
            self.entry_text = self.entry_text[0]
        if self.journal_entry.get('1.0'):
            self.journal_entry.delete('1.0',tk.END)
        if self.entry_text:
            self.journal_entry.insert(tk.END, self.entry_text)
        
    #save days data to database
    def save_day_data(self):
        self.day.entry = self.journal_entry.get('1.0',tk.END)
        
        for id in self.daily_goal_button_dict:
            button, state = self.daily_goal_button_dict[id]
            print(state)
            
            if self.day.goals[id]:
                self.day.goals[id][1] = state
       
        with JournalData() as journal_data:
            journal_data.check_if_date(self.day)

    
#standard check and start for the app
if __name__ == '__main__':
    root = tk.Tk()
    app = JournalApp(root)
    root.mainloop()