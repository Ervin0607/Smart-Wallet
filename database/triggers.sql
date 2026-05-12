DELIMITER $$

DROP TRIGGER IF EXISTS trg_update_budget_spent $$
DROP TRIGGER IF EXISTS trg_update_balances $$
DROP TRIGGER IF EXISTS trg_budget_warning $$
DROP TRIGGER IF EXISTS trg_budget_exceeded $$
DROP TRIGGER IF EXISTS trg_transaction_after_insert $$
DROP TRIGGER IF EXISTS trg_budget_status_update $$

CREATE TRIGGER trg_transaction_after_insert
AFTER INSERT ON Transaction
FOR EACH ROW
BEGIN
    DECLARE v_user_id INT;

    IF NEW.Status = 'COMPLETED' THEN

        IF NEW.PaymentMode = 'Wallet Balance' THEN
            UPDATE Wallet SET Balance = Balance - NEW.Amount WHERE WalletID = NEW.WalletID;
        END IF;

        SELECT UserID INTO v_user_id FROM Wallet WHERE WalletID = NEW.WalletID;

        IF NEW.PaymentMode IN ('Wallet Balance', 'Crypto Transfer', 'Bank Transfer') AND NEW.CategoryID != 9 AND NEW.PaymentMode != 'Received Transfer' THEN
            UPDATE Budget
            SET SpentAmount = SpentAmount + NEW.Amount
            WHERE UserID = v_user_id
              AND StartDate <= CURDATE()
              AND EndDate >= CURDATE();
        END IF;

    END IF;
END $$

CREATE TRIGGER trg_budget_status_update
BEFORE UPDATE ON Budget
FOR EACH ROW
BEGIN
    IF NEW.SpentAmount >= NEW.LimitAmount THEN
        SET NEW.Status = 'Exceeded';
        
        IF OLD.Status != 'Exceeded' THEN
            INSERT INTO Alert (BudgetID, AlertMessage, TriggerDate, IsREAD)
            VALUES (NEW.BudgetID, CONCAT('CRITICAL: Budget limit exceeded! Spent: ', NEW.SpentAmount, ' INR'), NOW(), FALSE);
        END IF;
        
    ELSEIF NEW.SpentAmount >= NEW.LimitAmount * 0.8 AND NEW.SpentAmount < NEW.LimitAmount THEN
        SET NEW.Status = 'Warning';
        
        IF OLD.Status = 'Active' THEN
            INSERT INTO Alert (BudgetID, AlertMessage, TriggerDate, IsREAD)
            VALUES (NEW.BudgetID, CONCAT('Warning: You have used more than 80% of your budget. Spent: ', NEW.SpentAmount, ' INR'), NOW(), FALSE);
        END IF;
        
    ELSEIF NEW.SpentAmount < NEW.LimitAmount * 0.8 THEN
        SET NEW.Status = 'Active';
    END IF;
END $$

DELIMITER ;