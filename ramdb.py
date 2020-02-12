# Реализация без сторонних пакетов
import sys, os
from collections import Counter

os.system('color')

class OP:
	NO_PARAMS	= 0x0
	WITH_PARAMS	= 0x1
	ONLY_VAL	= 0x2 | WITH_PARAMS
	WITH_VAL	= 0x4 | WITH_PARAMS

class TermColors:
    USAGE	= '\033[90m'
    USAGE	= '\033[90m'
    ERROR	= '\033[91m'
    DEFAULT = '\033[0m'

class setBase:
	def __init__(self):
		self.ramDB = {}
		self.tmpRec = self.newRec
		self.tmpRecList = []
		self._key = None
		self._val = 'NULL'

	@property
	def newRec(self):
		return dict({
			'set': 	{},
			'unset':	{}
		})

	@property
	def key(self):
		return self._key

	@key.setter
	def key(self, key):
		self._key = key

	@property
	def val(self):
		return self._val

	@val.setter
	def val(self, val):
		self._val = val

	@property
	def set_val(self):
		self.tmpRec['set'].update({self.key: self.val})
		self.tmpRec['unset'].pop(self.key, None)

	@property
	def get_val(self):
		if self.key == '*':
			return self.ramDB
		if self.key == '.':
			return f"set: {self.tmpRec['set']}" + '\n' + f"unset: {[_ for _ in self.tmpRec['unset']]}"
		if self.key == '..':
			toSet = [val['set'] for val in self.tmpRecList] + [self.tmpRec['set']]
			toUnset = []
			for tmp in db.tmpRecList:
				for key in tmp['unset'].keys():
					toUnset.append(key)
			toUnset += [_ for _ in self.tmpRec['unset']]
			return f"set: {toSet}" + '\n' + f"unset: {toUnset}"
		if self.key in self.tmpRec['set']:
			return self.tmpRec['set'][self.key]
		if self.key in self.tmpRec['unset']:
			return 'NULL'
		for tmp in self.tmpRecList[::-1]:
			if self.key in tmp['set']:
				return tmp['set'][self.key]
			if self.key in tmp['unset']:
				return 'NULL'
		return self.ramDB.get(self.key, 'NULL')

	@property
	def counts(self):
		toCount = self.tmpRec['set'].copy()
		for val in self.tmpRecList:
			toCount.update(val['set'])
		return Counter({**self.ramDB, **toCount}.values()).get(self.val, 0)

	@property
	def unset(self):
		if self.tmpRec['set'].pop(self.key, None) is None:
			self.tmpRec['unset'].update({self.key: None})

	@property
	def rollback(self):
		if self.tmpRecList:
			self.tmpRec = self.tmpRecList.pop()
		else:
			self.tmpRec.clear()
			self.tmpRec = self.newRec

	@property
	def commit(self):
		while self.tmpRecList:
			lastRec = self.tmpRecList.pop()
			for key, val in self.tmpRec['set'].items():
				lastRec['set'][key] = val
				lastRec['unset'].pop(key, None)
			unset = self.tmpRec['unset'].copy()
			for key in self.tmpRec['unset']:
				if lastRec['set'].pop(key, None) is not None:
					unset.pop(key)
			lastRec['unset'].update(unset)
			self.tmpRec.clear()
			self.tmpRec = lastRec
		for key, val in self.tmpRec['set'].items():
			self.ramDB[key] = val
		for key in self.tmpRec['unset']:
			self.ramDB.pop(key, None)
		self.tmpRec.clear()
		self.tmpRec = self.newRec

	@property
	def begin(self):
		self.tmpRecList.append(self.tmpRec.copy())
		self.tmpRec.clear()
		self.tmpRec = self.newRec

commandsList = {
	'set':		{
		'f':		lambda db:		db.set_val,
		'state':	OP.WITH_VAL
	},
	'get':		{
		'f':		lambda db:		print(db.get_val),
		'state':	OP.WITH_PARAMS
	},
	'counts':	{
		'f':		lambda db:		print(db.counts),
		'state':	OP.ONLY_VAL
	},
	'unset':	{
		'f':		lambda db:		db.unset,
		'state':	OP.WITH_PARAMS
	},
	'commit':	{
		'f':		lambda db:		db.commit,
		'state':	OP.NO_PARAMS
	},
	'begin':	{
		'f':		lambda db:		db.begin,
		'state':	OP.NO_PARAMS
	},
	'rollback':	{
		'f':		lambda db:		db.rollback,
		'state':	OP.NO_PARAMS
	}
}

def validation(db: setBase, args):
	err = ''
	argc = len(args)
	if args[0] not in commandsList:
		return f"{TermColors.ERROR}Error: command '{args[0]}' does not exist.{TermColors.DEFAULT}"
	if commandsList[args[0]]['state'] & OP.WITH_PARAMS == OP.WITH_PARAMS:
		key = commandsList[args[0]]['state'] & OP.ONLY_VAL != OP.ONLY_VAL
		if argc < 2:
			return f"{TermColors.ERROR}Error: argument{' name' if key else ''} is missing.{TermColors.DEFAULT}"
		if key and args[1] != '*' and args[1] != '.' and args[1] != '..' and \
			(not args[1].isalnum() or not args[1][0].isalpha()):
			return f"{TermColors.ERROR}Error: '{args[1]}' is invalid argument name.{TermColors.DEFAULT}"
		if key:
			if commandsList[args[0]]['state'] & OP.WITH_VAL == OP.WITH_VAL:
				if argc < 3:
					return f"{TermColors.ERROR}Error: argument is missing.{TermColors.DEFAULT}"
				db.val = args[2]
			db.key = args[1]
		else:
			db.val = args[1]
	return err

def usage():
	print(f"""Usage: {os.path.basename(__file__)} command [arg [val]]{TermColors.USAGE}
************************************************************************************
SET arg [val]   - set argument with name 'arg' to value 'val' (default: val = NULL),
GET arg         - get 'arg's value,
GET *           - show Database,
GET .           - show current transaction,
GET ..          - show all transactions,
UNSET arg       - delete argument with name 'arg',
COUNTS val      - count only set values in all transactions and values in Database,
BEGIN           - start new transaction,
ROLLBACK        - rollback current transaction's changes,
COMMIT          - commit all transaction's changes,
USAGE           - show usage,
HELP            - USAGE's alias,
.               - USAGE's alias,
CLS             - clear screen,
END             - drop Database and exit (CTRL + Z -> ENTER).{TermColors.DEFAULT}""")

additionalCommands = {
	'.':		lambda :	usage(),
	'help':		lambda :	usage(),
	'usage':	lambda :	usage(),
	'end':		lambda :	exit(),
	'cls':		lambda :	print('\033c')
}

if __name__ == '__main__':
	db = setBase()
	for line in sys.stdin:
		args = line.strip().lower().split(' ', 2)
		if not args[0]:
			continue
		if args[0] in additionalCommands:
			additionalCommands[args[0]]()
			continue
		err = validation(db, args)
		if err:
			print(err)
			continue
		commandsList[args[0]]['f'](db)