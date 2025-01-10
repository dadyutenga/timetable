-- Create the database
CREATE DATABASE UniversityTimetable;
USE UniversityTimetable;

-- Department Table (enhanced version)
CREATE TABLE Department (
    dept_id INT AUTO_INCREMENT PRIMARY KEY,
    dept_name VARCHAR(255) NOT NULL,
    dept_descr TEXT,
    hod VARCHAR(255),
    hod_phone VARCHAR(20),
    hod_email VARCHAR(254)
);

-- Program Table (enhanced version)
CREATE TABLE Program (
    program_id INT AUTO_INCREMENT PRIMARY KEY,
    program_name VARCHAR(255) NOT NULL,
    dept_id INT NOT NULL,
    nta_level VARCHAR(10),
    duration INT NOT NULL, -- Duration in semesters
    FOREIGN KEY (dept_id) REFERENCES Department(dept_id) ON DELETE CASCADE
);

-- Staff Table (replaces Instructors with more details)
CREATE TABLE Staff (
    staff_id INT AUTO_INCREMENT PRIMARY KEY,
    staff_name VARCHAR(255) NOT NULL,
    rfid_id VARCHAR(50),
    staff_email VARCHAR(254),
    staff_phone VARCHAR(20),
    staff_type VARCHAR(50) NOT NULL,
    staff_title VARCHAR(50),
    dept_id INT NOT NULL,
    user_id INT UNIQUE,
    FOREIGN KEY (dept_id) REFERENCES Department(dept_id) ON DELETE CASCADE
);

-- Module Table (enhanced version)
CREATE TABLE Module (
    module_id INT AUTO_INCREMENT PRIMARY KEY,
    module_code VARCHAR(50) NOT NULL,
    module_name VARCHAR(255) NOT NULL,
    program_id INT NOT NULL,
    module_type VARCHAR(50),
    module_year INT,
    semester INT,
    nta_level VARCHAR(10),
    credits INT NOT NULL,
    duration INT NOT NULL, -- Duration in hours
    FOREIGN KEY (program_id) REFERENCES Program(program_id) ON DELETE CASCADE
);

-- Room Table (enhanced version)
CREATE TABLE Room (
    room_id INT AUTO_INCREMENT PRIMARY KEY,
    room_name VARCHAR(255) NOT NULL,
    room_description TEXT,
    room_type ENUM('Lecture Hall', 'Lab', 'Seminar Room') NOT NULL,
    capacity INT NOT NULL,
    building_name VARCHAR(255) NOT NULL,
    room_no VARCHAR(50) NOT NULL,
    dept_id INT,
    FOREIGN KEY (dept_id) REFERENCES Department(dept_id) ON DELETE SET NULL
);

-- Class Table (new addition for better student group management)
CREATE TABLE Class (
    class_id INT AUTO_INCREMENT PRIMARY KEY,
    program_id INT NOT NULL,
    class_name VARCHAR(50) NOT NULL,
    class_capacity INT NOT NULL,
    academic_year VARCHAR(10) NOT NULL,
    class_stream VARCHAR(50) NOT NULL,
    FOREIGN KEY (program_id) REFERENCES Program(program_id) ON DELETE CASCADE
);

-- TeacherPreference Table (new addition for constraint-based scheduling)
CREATE TABLE TeacherPreference (
    preference_id INT AUTO_INCREMENT PRIMARY KEY,
    staff_id INT NOT NULL,
    day_of_week ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday') NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    preference_weight INT DEFAULT 1,
    FOREIGN KEY (staff_id) REFERENCES Staff(staff_id) ON DELETE CASCADE
);

-- ModuleAllocation Table (new addition for teacher-module assignments)
CREATE TABLE ModuleAllocation (
    allocation_id INT AUTO_INCREMENT PRIMARY KEY,
    module_id INT NOT NULL,
    staff_id INT NOT NULL,
    FOREIGN KEY (module_id) REFERENCES Module(module_id) ON DELETE CASCADE,
    FOREIGN KEY (staff_id) REFERENCES Staff(staff_id) ON DELETE CASCADE,
    UNIQUE (module_id, staff_id)
);

-- Timetable Table (enhanced version)
CREATE TABLE Timetable (
    timetable_id INT AUTO_INCREMENT PRIMARY KEY,
    module_id INT NOT NULL,
    room_id INT NOT NULL,
    staff_id INT NOT NULL,
    class_id INT NOT NULL,
    day_of_week ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday') NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    semester INT NOT NULL,
    academic_year VARCHAR(10) NOT NULL,
    FOREIGN KEY (module_id) REFERENCES Module(module_id) ON DELETE CASCADE,
    FOREIGN KEY (room_id) REFERENCES Room(room_id) ON DELETE CASCADE,
    FOREIGN KEY (staff_id) REFERENCES Staff(staff_id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES Class(class_id) ON DELETE CASCADE
);

-- Conflicts Table (for tracking scheduling conflicts)
CREATE TABLE Conflicts (
    conflict_id INT AUTO_INCREMENT PRIMARY KEY,
    timetable_id_1 INT NOT NULL,
    timetable_id_2 INT NOT NULL,
    conflict_type ENUM('Room', 'Teacher', 'Class') NOT NULL,
    conflict_description TEXT,
    FOREIGN KEY (timetable_id_1) REFERENCES Timetable(timetable_id) ON DELETE CASCADE,
    FOREIGN KEY (timetable_id_2) REFERENCES Timetable(timetable_id) ON DELETE CASCADE
);
