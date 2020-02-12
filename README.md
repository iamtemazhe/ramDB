# Список команд:
- SET arg val     - set argument with name 'arg' to value 'val'
- GET arg         - get 'arg's value
- GET *           - show Database
- GET .           - show current transaction
- GET ..          - show all transactions
- UNSET arg       - delete argument with name 'arg'
- COUNTS val      - count only set values in all transactions and values in Database
- BEGIN           - start new transaction
- ROLLBACK        - rollback current transaction's changes
- COMMIT          - commit all transaction's changes
- USAGE           - show usage
- HELP            - USAGE's alias
- .               - USAGE's alias
- CLS             - clear screen
- END             - drop Database and exit (CTRL + Z -> ENTER)

# Примечание:
Реализация на python без использования sqllite3 и других db-библиотек.

# Не дописан:
- парсер и проверки
- counts по всей DB с учетом транзакций