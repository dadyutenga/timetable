-- Department Table
CREATE TABLE Department (
    dept_id  INTEGER PRIMARY KEY,
    dept_name VARCHAR(255) NOT NULL,
    dept_descr TEXT,
    hod VARCHAR(255),
    hod_phone VARCHAR(20),
    hod_email VARCHAR(254)
);

-- Program Table
CREATE TABLE Program (
    program_id INTEGER PRIMARY KEY,
    program_name VARCHAR(255) NOT NULL,
    dept_id INTEGER NOT NULL,
    nta_level VARCHAR(10),
    FOREIGN KEY (dept_id) REFERENCES Department(dept_id) ON DELETE CASCADE
);

-- Module Table
CREATE TABLE Module (
    module_id INTEGER PRIMARY KEY,
    module_code VARCHAR(50) NOT NULL,
    module_name VARCHAR(255) NOT NULL,
    program_id INTEGER NOT NULL,
    module_type VARCHAR(50),
    module_year INTEGER,
    semester INTEGER,
    nta_level VARCHAR(10),
    FOREIGN KEY (program_id) REFERENCES Program(program_id) ON DELETE CASCADE
);

-- Room Table
CREATE TABLE Room (
    room_id INTEGER PRIMARY KEY,
    room_name VARCHAR(255) NOT NULL,
    room_description TEXT,
    room_type VARCHAR(50) NOT NULL,
    capacity INTEGER NOT NULL,
    building_name VARCHAR(255) NOT NULL,
    room_no VARCHAR(50) NOT NULL
);

-- Staff Table
CREATE TABLE Staff (
    staff_id INTEGER PRIMARY KEY,
    staff_name VARCHAR(255) NOT NULL,
    rfid_id VARCHAR(50),
    staff_email VARCHAR(254),
    staff_phone VARCHAR(20),
    staff_type VARCHAR(50) NOT NULL,
    staff_title VARCHAR(50),
    dept_id INTEGER NOT NULL,
    user_id INTEGER UNIQUE,
    FOREIGN KEY (dept_id) REFERENCES Department(dept_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
);

-- Timetable Table
CREATE TABLE Timetable (
    timetable_id INTEGER PRIMARY KEY,
    module_id INTEGER NOT NULL,
    room_id INTEGER NOT NULL,
    staff_id INTEGER NOT NULL,
    day_of_week VARCHAR(10) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    semester INTEGER NOT NULL,
    FOREIGN KEY (module_id) REFERENCES Module(module_id) ON DELETE CASCADE,
    FOREIGN KEY (room_id) REFERENCES Room(room_id) ON DELETE CASCADE,
    FOREIGN KEY (staff_id) REFERENCES Staff(staff_id) ON DELETE CASCADE
);

CREATE TABLE TeacherPreference (
    id INTEGER PRIMARY KEY,
    staff_id INTEGER NOT NULL,
    day_of_week VARCHAR(10) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    preference_weight INTEGER DEFAULT 1,
    FOREIGN KEY (staff_id) REFERENCES Staff(staff_id) ON DELETE CASCADE
);

-- ModuleAllocation Table
CREATE TABLE ModuleAllocation (
    allocation_id INTEGER PRIMARY KEY,
    module_id INTEGER NOT NULL,
    staff_id INTEGER NOT NULL,
    FOREIGN KEY (module_id) REFERENCES Module(module_id) ON DELETE CASCADE,
    FOREIGN KEY (staff_id) REFERENCES Staff(staff_id) ON DELETE CASCADE,
    UNIQUE (module_id, staff_id)
);

-- Class Table
CREATE TABLE Class (
    program_id  INTEGER NOT NULL,
    Class_id INTEGER PRIMARY KEY,
    Class_name  VARCHAR(50) NOT NULL,
    class_capacity INTEGER NOT NULL,
    academic_year VARCHAR(10) NOT NULL,
    class_stream VARCHAR(50) NOT NULL,
    FOREIGN KEY (program_id) REFERENCES Program(program_id) ON DELETE CASCADE
);