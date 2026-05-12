-- Smart Wallet with Budget Guardian

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS Alert;
DROP TABLE IF EXISTS Transaction;
DROP TABLE IF EXISTS CryptoAsset;
DROP TABLE IF EXISTS SupportedCrypto;
DROP TABLE IF EXISTS Budget;
DROP TABLE IF EXISTS BankAccount;
DROP TABLE IF EXISTS Wallet;
DROP TABLE IF EXISTS Category;
DROP TABLE IF EXISTS DummyBank;
DROP TABLE IF EXISTS User;

SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE DummyBank (
    DummyAccountID INT AUTO_INCREMENT PRIMARY KEY,
    AccountNumber  VARCHAR(30) NOT NULL UNIQUE,
    BankName       VARCHAR(100),
    IFSC_Code      VARCHAR(20),
    InitialBalance DECIMAL(15,2) DEFAULT 0.00
);

CREATE TABLE User (
    UserID       INT           AUTO_INCREMENT PRIMARY KEY,
    Name         VARCHAR(100)  NOT NULL,
    Email        VARCHAR(100)  NOT NULL,
    PasswordHash VARCHAR(255)  NOT NULL,
    Phone        VARCHAR(15),
    CONSTRAINT uq_user_email UNIQUE (Email)
);

CREATE TABLE Category (
    CategoryID   INT          AUTO_INCREMENT PRIMARY KEY,
    CategoryName VARCHAR(100) NOT NULL,
    PriorityLevel VARCHAR(50)
);


CREATE TABLE Wallet (
    WalletID    INT            AUTO_INCREMENT PRIMARY KEY,
    UserID      INT            NOT NULL,
    Balance     DECIMAL(15,2)  DEFAULT 0.00,
    Currency    VARCHAR(10)    DEFAULT 'INR',
    LastUpdated TIMESTAMP      DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_wallet_user FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE
);


CREATE TABLE BankAccount (
    AccountID     INT          AUTO_INCREMENT PRIMARY KEY,
    UserID        INT          NULL,
    WalletID      INT          NULL,
    AccountNumber VARCHAR(30)  NOT NULL,
    BankName      VARCHAR(100),
    IFSC_Code     VARCHAR(20),
    BankBalance   DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    CONSTRAINT fk_bankaccount_user   FOREIGN KEY (UserID)   REFERENCES User(UserID)     ON DELETE CASCADE,
    CONSTRAINT fk_bankaccount_wallet FOREIGN KEY (WalletID) REFERENCES Wallet(WalletID) ON DELETE CASCADE
);


CREATE TABLE Budget (
    BudgetID    INT           AUTO_INCREMENT PRIMARY KEY,
    UserID      INT           NOT NULL,
    LimitAmount DECIMAL(15,2) NOT NULL,
    SpentAmount DECIMAL(15,2) DEFAULT 0.00,
    StartDate   DATE          NOT NULL,
    EndDate     DATE          NOT NULL,
    Status      VARCHAR(20)   DEFAULT 'Active',
    CONSTRAINT fk_budget_user FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE
);

CREATE TABLE SupportedCrypto (
    CryptoID        INT           AUTO_INCREMENT PRIMARY KEY,
    Symbol          VARCHAR(10)   NOT NULL,
    CryptoName      VARCHAR(100)  NOT NULL,
    LiveMarketPrice DECIMAL(20,8) NOT NULL DEFAULT 0,
    LastUpdated     TIMESTAMP     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_crypto_symbol UNIQUE (Symbol)
);


CREATE TABLE CryptoAsset (
    AssetID  INT           NOT NULL,
    WalletID INT           NOT NULL,
    Quantity DECIMAL(20,8) NOT NULL DEFAULT 0,
    PRIMARY KEY (AssetID, WalletID),
    CONSTRAINT fk_cryptoasset_crypto  FOREIGN KEY (AssetID)  REFERENCES SupportedCrypto(CryptoID) ON DELETE CASCADE,
    CONSTRAINT fk_cryptoasset_wallet  FOREIGN KEY (WalletID) REFERENCES Wallet(WalletID)           ON DELETE CASCADE
);


CREATE TABLE Transaction (
    TransactionID   INT           AUTO_INCREMENT PRIMARY KEY,
    WalletID        INT           NULL,
    CategoryID      INT           NOT NULL,
    Amount          DECIMAL(15,2) NOT NULL,
    TransactionDate TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
    PaymentMode     VARCHAR(50)   NOT NULL DEFAULT 'Wallet Balance',
    AccountID       INT           NULL,
    AssetID         INT           NULL,
    Status          VARCHAR(20)   DEFAULT 'pending',
    CONSTRAINT fk_txn_wallet   FOREIGN KEY (WalletID)   REFERENCES Wallet(WalletID)         ON DELETE SET NULL,
    CONSTRAINT fk_txn_category FOREIGN KEY (CategoryID) REFERENCES Category(CategoryID),
    CONSTRAINT fk_txn_account  FOREIGN KEY (AccountID)  REFERENCES BankAccount(AccountID)    ON DELETE SET NULL,
    CONSTRAINT fk_txn_asset    FOREIGN KEY (AssetID)    REFERENCES SupportedCrypto(CryptoID) ON DELETE SET NULL
);

CREATE TABLE Alert (
    AlertID     INT       AUTO_INCREMENT PRIMARY KEY,
    BudgetID    INT       NOT NULL,
    AlertMessage TEXT,
    TriggerDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    IsREAD      BOOLEAN   DEFAULT FALSE,
    CONSTRAINT fk_alert_budget FOREIGN KEY (BudgetID) REFERENCES Budget(BudgetID) ON DELETE CASCADE
);


-- Indexes
CREATE UNIQUE INDEX idx_user_email       ON User(Email);
CREATE        INDEX idx_wallet_userid    ON Wallet(UserID);
CREATE        INDEX idx_txn_walletid     ON Transaction(WalletID);
CREATE        INDEX idx_txn_categoryid   ON Transaction(CategoryID);
CREATE        INDEX idx_txn_date         ON Transaction(TransactionDate);

-- View
CREATE OR REPLACE VIEW UserBalances AS
    SELECT u.Name, w.Balance, w.Currency
    FROM   User u
    JOIN   Wallet w ON u.UserID = w.UserID;

-- Seed: default categories
INSERT INTO Category (CategoryName, PriorityLevel) VALUES
    ('Food & Dining',   'High'),
    ('Transport',       'Medium'),
    ('Shopping',        'Medium'),
    ('Entertainment',   'Low'),
    ('Healthcare',      'High'),
    ('Utilities',       'High'),
    ('Travel',          'Low'),
    ('Crypto Purchase', 'Medium'),
    ('Wallet Top-Up',   'High'),
    ('Other',           'Low');

-- Seed: supported cryptocurrencies
INSERT INTO SupportedCrypto (Symbol, CryptoName, LiveMarketPrice) VALUES
    ('BTC', 'Bitcoin',  0),
    ('ETH', 'Ethereum', 0),
    ('SOL', 'Solana',   0),
    ('ADA', 'Cardano',  0),
    ('XRP', 'Ripple',   0);
