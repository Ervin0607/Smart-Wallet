-- DUMMY BANK ACCOUNTS FOR REGISTRATION
INSERT INTO DummyBank (AccountNumber, BankName, IFSC_Code, InitialBalance) VALUES
('DBNK1001', 'HDFC Bank',  'HDFC0021', 40000),
('DBNK1002', 'ICICI Bank', 'ICIC0022', 55000),
('DBNK1003', 'SBI',        'SBIN0023', 32000),
('DBNK1004', 'Axis Bank',  'UTIB0024', 48000),
('DBNK1005', 'Kotak Bank', 'KKBK0025', 27000);

-- USERS
INSERT INTO User (Name, Email, PasswordHash, Phone) VALUES
('Aarav Sharma','aarav@wallet.com','$2b$12$RQE/L11VSx2v0qkny5mMeO59WEVEjLWFnmLJF2D5at3U3qo6Fp7ei','987650001'),
('Vihaan Mehta','vihaan@wallet.com','$2b$12$RQE/L11VSx2v0qkny5mMeO59WEVEjLWFnmLJF2D5at3U3qo6Fp7ei','987650002'),
('Aditya Singh','aditya@wallet.com','$2b$12$RQE/L11VSx2v0qkny5mMeO59WEVEjLWFnmLJF2D5at3U3qo6Fp7ei','987650003'),
('Rohan Gupta','rohan@wallet.com','$2b$12$RQE/L11VSx2v0qkny5mMeO59WEVEjLWFnmLJF2D5at3U3qo6Fp7ei','987650004'),
('Kabir Jain','kabir@wallet.com','$2b$12$RQE/L11VSx2v0qkny5mMeO59WEVEjLWFnmLJF2D5at3U3qo6Fp7ei','987650005'),
('Arjun Kapoor','arjun@wallet.com','$2b$12$RQE/L11VSx2v0qkny5mMeO59WEVEjLWFnmLJF2D5at3U3qo6Fp7ei','987650006'),
('Aryan Patel','aryan@wallet.com','$2b$12$RQE/L11VSx2v0qkny5mMeO59WEVEjLWFnmLJF2D5at3U3qo6Fp7ei','987650007'),
('Karan Shah','karan@wallet.com','$2b$12$RQE/L11VSx2v0qkny5mMeO59WEVEjLWFnmLJF2D5at3U3qo6Fp7ei','987650008'),
('Ishaan Verma','ishaan@wallet.com','$2b$12$RQE/L11VSx2v0qkny5mMeO59WEVEjLWFnmLJF2D5at3U3qo6Fp7ei','987650009'),
('Dev Malhotra','dev@wallet.com','$2b$12$RQE/L11VSx2v0qkny5mMeO59WEVEjLWFnmLJF2D5at3U3qo6Fp7ei','987650010'),
('Riya Sharma','riya@wallet.com','$2b$12$RQE/L11VSx2v0qkny5mMeO59WEVEjLWFnmLJF2D5at3U3qo6Fp7ei','987650011'),
('Ananya Gupta','ananya@wallet.com','$2b$12$RQE/L11VSx2v0qkny5mMeO59WEVEjLWFnmLJF2D5at3U3qo6Fp7ei','987650012'),
('Aditi Mehta','aditi@wallet.com','$2b$12$RQE/L11VSx2v0qkny5mMeO59WEVEjLWFnmLJF2D5at3U3qo6Fp7ei','987650013'),
('Priya Singh','priya@wallet.com','$2b$12$RQE/L11VSx2v0qkny5mMeO59WEVEjLWFnmLJF2D5at3U3qo6Fp7ei','987650014'),
('Neha Kapoor','neha@wallet.com','$2b$12$RQE/L11VSx2v0qkny5mMeO59WEVEjLWFnmLJF2D5at3U3qo6Fp7ei','987650015'),
('Sara Khan','sara@wallet.com','$2b$12$RQE/L11VSx2v0qkny5mMeO59WEVEjLWFnmLJF2D5at3U3qo6Fp7ei','987650016'),
('Meera Iyer','meera@wallet.com','$2b$12$RQE/L11VSx2v0qkny5mMeO59WEVEjLWFnmLJF2D5at3U3qo6Fp7ei','987650017'),
('Pooja Shah','pooja@wallet.com','$2b$12$RQE/L11VSx2v0qkny5mMeO59WEVEjLWFnmLJF2D5at3U3qo6Fp7ei','987650018'),
('Sneha Nair','sneha@wallet.com','$2b$12$RQE/L11VSx2v0qkny5mMeO59WEVEjLWFnmLJF2D5at3U3qo6Fp7ei','987650019'),
('Tanvi Rao','tanvi@wallet.com','$2b$12$RQE/L11VSx2v0qkny5mMeO59WEVEjLWFnmLJF2D5at3U3qo6Fp7ei','987650020');

INSERT INTO Wallet (UserID, Balance, Currency) VALUES
(1,5000,'INR'),
(2,12000,'INR'),
(3,8500,'INR'),
(4,23000,'INR'),
(5,9200,'INR'),
(6,4000,'INR'),
(7,15000,'INR'),
(8,8000,'INR'),
(9,12500,'INR'),
(10,3000,'INR'),
(11,5400,'INR'),
(12,21000,'INR'),
(13,9800,'INR'),
(14,7300,'INR'),
(15,6100,'INR'),
(16,17500,'INR'),
(17,9100,'INR'),
(18,14200,'INR'),
(19,4600,'INR'),
(20,8800,'INR');

INSERT INTO BankAccount (UserID, WalletID, AccountNumber, BankName, IFSC_Code, BankBalance) VALUES
(1,1,'ACC1001','HDFC Bank','HDFC0001',50000),
(2,2,'ACC1002','ICICI Bank','ICIC0002',42000),
(3,3,'ACC1003','SBI','SBIN0003',30000),
(4,4,'ACC1004','Axis Bank','UTIB0004',62000),
(5,5,'ACC1005','Kotak Bank','KKBK0005',51000),
(6,6,'ACC1006','HDFC Bank','HDFC0006',25000),
(7,7,'ACC1007','ICICI Bank','ICIC0007',47000),
(8,8,'ACC1008','SBI','SBIN0008',38000),
(9,9,'ACC1009','Axis Bank','UTIB0009',54000),
(10,10,'ACC1010','Kotak Bank','KKBK0010',19000),
(11,11,'ACC1011','HDFC Bank','HDFC0011',33000),
(12,12,'ACC1012','ICICI Bank','ICIC0012',75000),
(13,13,'ACC1013','SBI','SBIN0013',28000),
(14,14,'ACC1014','Axis Bank','UTIB0014',36000),
(15,15,'ACC1015','Kotak Bank','KKBK0015',22000),
(16,16,'ACC1016','HDFC Bank','HDFC0016',68000),
(17,17,'ACC1017','ICICI Bank','ICIC0017',41000),
(18,18,'ACC1018','SBI','SBIN0018',35000),
(19,19,'ACC1019','Axis Bank','UTIB0019',26000),
(20,20,'ACC1020','Kotak Bank','KKBK0020',30000);

-- UNLINKED BANK ACCOUNTS (available for new user registration)
INSERT INTO BankAccount (UserID, WalletID, AccountNumber, BankName, IFSC_Code, BankBalance) VALUES
(NULL, NULL, 'ACC2001', 'HDFC Bank',  'HDFC0021', 40000),
(NULL, NULL, 'ACC2002', 'ICICI Bank', 'ICIC0022', 55000),
(NULL, NULL, 'ACC2003', 'SBI',        'SBIN0023', 32000),
(NULL, NULL, 'ACC2004', 'Axis Bank',  'UTIB0024', 48000),
(NULL, NULL, 'ACC2005', 'Kotak Bank', 'KKBK0025', 27000);

INSERT INTO Budget (UserID, LimitAmount, SpentAmount, StartDate, EndDate, Status) VALUES
(1,10000,2000,'2026-03-01','2026-03-31','Active'),
(2,15000,8000,'2026-03-01','2026-03-31','Active'),
(3,12000,6000,'2026-03-01','2026-03-31','Active'),
(4,20000,14000,'2026-03-01','2026-03-31','Warning'),
(5,9000,7000,'2026-03-01','2026-03-31','Warning'),
(6,8000,7500,'2026-03-01','2026-03-31','Warning'),
(7,25000,12000,'2026-03-01','2026-03-31','Active'),
(8,10000,9500,'2026-03-01','2026-03-31','Warning'),
(9,13000,11000,'2026-03-01','2026-03-31','Warning'),
(10,7000,7200,'2026-03-01','2026-03-31','Exceeded'),
(11,9000,5000,'2026-03-01','2026-03-31','Active'),
(12,18000,16000,'2026-03-01','2026-03-31','Warning'),
(13,11000,4000,'2026-03-01','2026-03-31','Active'),
(14,8000,3000,'2026-03-01','2026-03-31','Active'),
(15,7500,7600,'2026-03-01','2026-03-31','Exceeded'),
(16,20000,10000,'2026-03-01','2026-03-31','Active'),
(17,9500,9200,'2026-03-01','2026-03-31','Warning'),
(18,14000,10000,'2026-03-01','2026-03-31','Active'),
(19,6000,5900,'2026-03-01','2026-03-31','Warning'),
(20,10000,5000,'2026-03-01','2026-03-31','Active');

INSERT INTO CryptoAsset (AssetID, WalletID, Quantity) VALUES
(1,1,0.002),
(2,2,0.5),
(3,3,12),
(4,4,500),
(5,5,800),
(1,6,0.01),
(2,7,1.2),
(3,8,5),
(4,9,250),
(5,10,300);

INSERT INTO Transaction (WalletID, CategoryID, Amount, PaymentMode, Status) VALUES
(1,1,500,'Wallet Balance','completed'),
(2,2,300,'Wallet Balance','completed'),
(3,3,1200,'Wallet Balance','completed'),
(4,4,800,'Wallet Balance','completed'),
(5,1,250,'Wallet Balance','completed'),
(6,6,400,'Wallet Balance','completed'),
(7,2,1500,'Wallet Balance','completed'),
(8,1,350,'Wallet Balance','completed'),
(9,5,600,'Wallet Balance','completed'),
(10,7,900,'Wallet Balance','completed'),
(11,3,700,'Wallet Balance','completed'),
(12,2,450,'Wallet Balance','completed'),
(13,4,1100,'Wallet Balance','completed'),
(14,6,500,'Wallet Balance','completed'),
(15,1,300,'Wallet Balance','completed'),
(16,3,950,'Wallet Balance','completed'),
(17,7,1400,'Wallet Balance','completed'),
(18,5,650,'Wallet Balance','completed'),
(19,2,720,'Wallet Balance','completed'),
(20,4,550,'Wallet Balance','completed'),
(1,8,1000,'Wallet Balance','completed'),
(2,8,1500,'Wallet Balance','completed'),
(3,8,2000,'Wallet Balance','completed'),
(4,8,2500,'Wallet Balance','completed'),
(5,8,3000,'Wallet Balance','completed');

INSERT INTO Alert (BudgetID, AlertMessage, IsREAD) VALUES
(4,'80% of budget used',FALSE),
(5,'Budget almost exceeded',FALSE),
(6,'Budget almost exceeded',FALSE),
(10,'Budget exceeded!',FALSE),
(15,'Budget exceeded!',FALSE);

