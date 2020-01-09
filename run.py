import main as fx

financeobj = fx.main()
summary = financeobj.create_quote(amount=500000)

print(summary)

financeobj.clear_quotes()
