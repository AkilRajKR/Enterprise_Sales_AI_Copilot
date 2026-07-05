-- Initial seed data for Enterprise Sales AI Copilot
-- Insert sample brands
INSERT INTO Brands (brand_name) VALUES ('Tesla');
INSERT INTO Brands (brand_name) VALUES ('BMW');
INSERT INTO Brands (brand_name) VALUES ('Mercedes-Benz');
INSERT INTO Brands (brand_name) VALUES ('Audi');
INSERT INTO Brands (brand_name) VALUES ('Volkswagen');
INSERT INTO Brands (brand_name) VALUES ('Ford');
INSERT INTO Brands (brand_name) VALUES ('Toyota');
INSERT INTO Brands (brand_name) VALUES ('Honda');
INSERT INTO Brands (brand_name) VALUES ('Hyundai');
INSERT INTO Brands (brand_name) VALUES ('Kia');

-- Insert manufacture plants
INSERT INTO Manufacture_Plant (plant_name, plant_type, plant_location, company_owned) VALUES ('Austin Assembly', 'Assembly', 'Austin, TX', 1);
INSERT INTO Manufacture_Plant (plant_name, plant_type, plant_location, company_owned) VALUES ('Berlin Parts', 'Parts', 'Berlin, Germany', 1);
INSERT INTO Manufacture_Plant (plant_name, plant_type, plant_location, company_owned) VALUES ('Stuttgart Assembly', 'Assembly', 'Stuttgart, Germany', 1);
INSERT INTO Manufacture_Plant (plant_name, plant_type, plant_location, company_owned) VALUES ('Ingolstadt Parts', 'Parts', 'Ingolstadt, Germany', 1);
INSERT INTO Manufacture_Plant (plant_name, plant_type, plant_location, company_owned) VALUES ('Wolfsburg Assembly', 'Assembly', 'Wolfsburg, Germany', 1);

-- Insert dealers
INSERT INTO Dealers (dealer_name, dealer_address) VALUES ('Downtown Motors', '123 Main St, New York, NY');
INSERT INTO Dealers (dealer_name, dealer_address) VALUES ('Premium Auto Sales', '456 Park Ave, Los Angeles, CA');
INSERT INTO Dealers (dealer_name, dealer_address) VALUES ('Elite Vehicles', '789 Commerce St, Chicago, IL');
INSERT INTO Dealers (dealer_name, dealer_address) VALUES ('Luxury Autos', '321 Luxury Ln, Miami, FL');
INSERT INTO Dealers (dealer_name, dealer_address) VALUES ('Tech Motors', '654 Innovation Blvd, San Francisco, CA');

-- Insert car models
INSERT INTO Models (model_name, model_base_price, brand_id) VALUES ('Model S', 79990, 1);
INSERT INTO Models (model_name, model_base_price, brand_id) VALUES ('Model 3', 42990, 1);
INSERT INTO Models (model_name, model_base_price, brand_id) VALUES ('3 Series', 45000, 2);
INSERT INTO Models (model_name, model_base_price, brand_id) VALUES ('5 Series', 60000, 2);
INSERT INTO Models (model_name, model_base_price, brand_id) VALUES ('C-Class', 50000, 3);
INSERT INTO Models (model_name, model_base_price, brand_id) VALUES ('E-Class', 65000, 3);
INSERT INTO Models (model_name, model_base_price, brand_id) VALUES ('A4', 48000, 4);
INSERT INTO Models (model_name, model_base_price, brand_id) VALUES ('A6', 62000, 4);
INSERT INTO Models (model_name, model_base_price, brand_id) VALUES ('Jetta', 25000, 5);
INSERT INTO Models (model_name, model_base_price, brand_id) VALUES ('Passat', 35000, 5);

-- Insert car parts
INSERT INTO Car_Parts (part_name, manufacture_plant_id, manufacture_start_date, manufacture_end_date, part_recall) VALUES ('Electric Motor V3', 1, '2023-01-15', NULL, 0);
INSERT INTO Car_Parts (part_name, manufacture_plant_id, manufacture_start_date, manufacture_end_date, part_recall) VALUES ('Dual Motor Assembly', 1, '2022-06-01', NULL, 0);
INSERT INTO Car_Parts (part_name, manufacture_plant_id, manufacture_start_date, manufacture_end_date, part_recall) VALUES ('Gasoline Engine 3.0L', 2, '2020-01-01', NULL, 0);
INSERT INTO Car_Parts (part_name, manufacture_plant_id, manufacture_start_date, manufacture_end_date, part_recall) VALUES ('Diesel Engine 2.0L', 2, '2021-03-01', NULL, 0);
INSERT INTO Car_Parts (part_name, manufacture_plant_id, manufacture_start_date, manufacture_end_date, part_recall) VALUES ('Automatic Transmission 8-Speed', 3, '2022-01-01', NULL, 0);
INSERT INTO Car_Parts (part_name, manufacture_plant_id, manufacture_start_date, manufacture_end_date, part_recall) VALUES ('Manual Transmission 6-Speed', 3, '2021-01-01', NULL, 0);
INSERT INTO Car_Parts (part_name, manufacture_plant_id, manufacture_start_date, manufacture_end_date, part_recall) VALUES ('Steel Chassis', 4, '2022-01-01', NULL, 0);
INSERT INTO Car_Parts (part_name, manufacture_plant_id, manufacture_start_date, manufacture_end_date, part_recall) VALUES ('Aluminum Chassis', 4, '2023-01-01', NULL, 0);
INSERT INTO Car_Parts (part_name, manufacture_plant_id, manufacture_start_date, manufacture_end_date, part_recall) VALUES ('Premium Sound System', 5, '2023-01-01', NULL, 0);
INSERT INTO Car_Parts (part_name, manufacture_plant_id, manufacture_start_date, manufacture_end_date, part_recall) VALUES ('Standard Sound System', 5, '2022-01-01', NULL, 0);

-- Insert car options
INSERT INTO Car_Options (model_id, engine_id, transmission_id, chassis_id, premium_sound_id, color, option_set_price) VALUES (1, 1, 5, 8, 9, 'Black', 5000);
INSERT INTO Car_Options (model_id, engine_id, transmission_id, chassis_id, premium_sound_id, color, option_set_price) VALUES (1, 2, 5, 7, 9, 'White', 7500);
INSERT INTO Car_Options (model_id, engine_id, transmission_id, chassis_id, premium_sound_id, color, option_set_price) VALUES (2, 1, 5, 8, NULL, 'Red', 3000);
INSERT INTO Car_Options (model_id, engine_id, transmission_id, chassis_id, premium_sound_id, color, option_set_price) VALUES (3, 3, 5, 7, 9, 'Blue', 4000);
INSERT INTO Car_Options (model_id, engine_id, transmission_id, chassis_id, premium_sound_id, color, option_set_price) VALUES (4, 4, 5, 8, 9, 'Silver', 5500);
INSERT INTO Car_Options (model_id, engine_id, transmission_id, chassis_id, premium_sound_id, color, option_set_price) VALUES (5, 3, 6, 7, NULL, 'Gray', 3500);
INSERT INTO Car_Options (model_id, engine_id, transmission_id, chassis_id, premium_sound_id, color, option_set_price) VALUES (6, 4, 5, 8, 9, 'Black', 6000);
INSERT INTO Car_Options (model_id, engine_id, transmission_id, chassis_id, premium_sound_id, color, option_set_price) VALUES (7, 3, 5, 7, 9, 'White', 4500);
INSERT INTO Car_Options (model_id, engine_id, transmission_id, chassis_id, premium_sound_id, color, option_set_price) VALUES (8, 4, 6, 8, 9, 'Blue', 5500);
INSERT INTO Car_Options (model_id, engine_id, transmission_id, chassis_id, premium_sound_id, color, option_set_price) VALUES (9, 3, 5, 7, NULL, 'Red', 2000);

-- Insert car VINs
INSERT INTO Car_Vins (model_id, option_set_id, manufactured_date, manufactured_plant_id) VALUES (1, 1, '2024-01-15', 1);
INSERT INTO Car_Vins (model_id, option_set_id, manufactured_date, manufactured_plant_id) VALUES (1, 2, '2024-02-20', 1);
INSERT INTO Car_Vins (model_id, option_set_id, manufactured_date, manufactured_plant_id) VALUES (2, 3, '2024-01-10', 1);
INSERT INTO Car_Vins (model_id, option_set_id, manufactured_date, manufactured_plant_id) VALUES (3, 4, '2024-02-15', 3);
INSERT INTO Car_Vins (model_id, option_set_id, manufactured_date, manufactured_plant_id) VALUES (4, 5, '2024-01-20', 3);
INSERT INTO Car_Vins (model_id, option_set_id, manufactured_date, manufactured_plant_id) VALUES (5, 6, '2024-02-10', 3);
INSERT INTO Car_Vins (model_id, option_set_id, manufactured_date, manufactured_plant_id) VALUES (6, 7, '2024-01-25', 3);
INSERT INTO Car_Vins (model_id, option_set_id, manufactured_date, manufactured_plant_id) VALUES (7, 8, '2024-02-05', 5);
INSERT INTO Car_Vins (model_id, option_set_id, manufactured_date, manufactured_plant_id) VALUES (8, 9, '2024-01-30', 5);
INSERT INTO Car_Vins (model_id, option_set_id, manufactured_date, manufactured_plant_id) VALUES (9, 10, '2024-02-12', 5);

-- Insert customers
INSERT INTO Customers (first_name, last_name, gender, household_income, birthdate, phone_number, email) VALUES ('John', 'Doe', 'Male', 85000, '1985-05-15', '5551234567', 'john.doe@email.com');
INSERT INTO Customers (first_name, last_name, gender, household_income, birthdate, phone_number, email) VALUES ('Jane', 'Smith', 'Female', 95000, '1988-08-22', '5559876543', 'jane.smith@email.com');
INSERT INTO Customers (first_name, last_name, gender, household_income, birthdate, phone_number, email) VALUES ('Michael', 'Johnson', 'Male', 120000, '1980-03-10', '5555551234', 'michael.j@email.com');
INSERT INTO Customers (first_name, last_name, gender, household_income, birthdate, phone_number, email) VALUES ('Sarah', 'Williams', 'Female', 110000, '1990-11-25', '5554449999', 'sarah.w@email.com');
INSERT INTO Customers (first_name, last_name, gender, household_income, birthdate, phone_number, email) VALUES ('Robert', 'Brown', 'Male', 75000, '1992-07-08', '5557778888', 'robert.b@email.com');

-- Insert dealer brands (associations)
INSERT INTO Dealer_Brand (dealer_id, brand_id) VALUES (1, 1);
INSERT INTO Dealer_Brand (dealer_id, brand_id) VALUES (1, 2);
INSERT INTO Dealer_Brand (dealer_id, brand_id) VALUES (2, 3);
INSERT INTO Dealer_Brand (dealer_id, brand_id) VALUES (2, 4);
INSERT INTO Dealer_Brand (dealer_id, brand_id) VALUES (3, 5);
INSERT INTO Dealer_Brand (dealer_id, brand_id) VALUES (3, 6);
INSERT INTO Dealer_Brand (dealer_id, brand_id) VALUES (4, 7);
INSERT INTO Dealer_Brand (dealer_id, brand_id) VALUES (4, 8);
INSERT INTO Dealer_Brand (dealer_id, brand_id) VALUES (5, 9);
INSERT INTO Dealer_Brand (dealer_id, brand_id) VALUES (5, 10);

-- Insert customer ownership records
INSERT INTO Customer_Ownership (customer_id, vin, purchase_date, purchase_price, warantee_expire_date, dealer_id) VALUES (1, 1, '2024-01-20', 85000, '2029-01-20', 1);
INSERT INTO Customer_Ownership (customer_id, vin, purchase_date, purchase_price, warantee_expire_date, dealer_id) VALUES (2, 2, '2024-02-25', 90000, '2029-02-25', 1);
INSERT INTO Customer_Ownership (customer_id, vin, purchase_date, purchase_price, warantee_expire_date, dealer_id) VALUES (3, 3, '2024-01-15', 48000, '2029-01-15', 2);
INSERT INTO Customer_Ownership (customer_id, vin, purchase_date, purchase_price, warantee_expire_date, dealer_id) VALUES (4, 4, '2024-02-20', 52000, '2029-02-20', 2);
INSERT INTO Customer_Ownership (customer_id, vin, purchase_date, purchase_price, warantee_expire_date, dealer_id) VALUES (5, 5, '2024-01-25', 68000, '2029-01-25', 3);
