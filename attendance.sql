CREATE TABLE IF NOT EXISTS public.attendance
(
    attendance_id serial NOT NULL,
    student_id integer,
    room_id integer,
    check_in_time timestamp without time zone,
    CONSTRAINT attendance_pkey PRIMARY KEY (attendance_id)
);

CREATE TABLE IF NOT EXISTS public.curriculum
(
    curriculum_id serial NOT NULL,
    course_code character varying(20) COLLATE pg_catalog."default",
    course_name character varying(255) COLLATE pg_catalog."default",
    program_id integer,
    semester integer,
    CONSTRAINT curriculum_pkey PRIMARY KEY (curriculum_id)
);

CREATE TABLE IF NOT EXISTS public.datasets
(
    auto_id serial NOT NULL,
    student_id integer,
    full_name character varying(200) COLLATE pg_catalog."default",
    number_of_images character varying(100) COLLATE pg_catalog."default",
    created_date character varying(50) COLLATE pg_catalog."default",
    CONSTRAINT datasets_pkey PRIMARY KEY (auto_id)
);




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

CREATE TABLE IF NOT EXISTS public.students
(
    student_id serial NOT NULL,
    first_name character varying(255) COLLATE pg_catalog."default",
    last_name character varying(255) COLLATE pg_catalog."default",
    email character varying(255) COLLATE pg_catalog."default",
    phone character varying(20) COLLATE pg_catalog."default",
    program_id  INTEGER NOT NULL,
    Class_id INTEGER PRIMARY KEY,
    CONSTRAINT students_pkey PRIMARY KEY (student_id)
    FOREIGN KEY (program_id) REFERENCES Program(program_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS public.training
(
    auto_id serial NOT NULL,
    student_id integer,
    full_name character varying(255) COLLATE pg_catalog."default",
    number_of_trained_images integer,
    trained_date date,
    model_data bytea,
    captured_images jsonb,
    CONSTRAINT training_pkey PRIMARY KEY (auto_id)
);

ALTER TABLE IF EXISTS public.attendance
    ADD CONSTRAINT attendance_room_id_fkey FOREIGN KEY (room_id)
    REFERENCES public.rooms (room_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public.attendance
    ADD CONSTRAINT attendance_student_id_fkey FOREIGN KEY (student_id)
    REFERENCES public.students (student_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public.curriculum
    ADD CONSTRAINT curriculum_program_id_fkey FOREIGN KEY (program_id)
    REFERENCES public.programs (program_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public.datasets
    ADD CONSTRAINT datasets_student_id_fkey FOREIGN KEY (student_id)
    REFERENCES public.students (student_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public.students
    ADD CONSTRAINT students_program_id_fkey FOREIGN KEY (program_id)
    REFERENCES public.programs (program_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public.training
    ADD CONSTRAINT training_student_id_fkey FOREIGN KEY (student_id)
    REFERENCES public.students (student_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

END;
