import hashlib

#Предположим, это отхэшированный список транзакций
Tx_hashlist = ['A100', 'B200', 'C300', 'D400',
			   'E500', 'F600', 'G700', 'H800'
			  ]
#Структура в которой будут храниться отхэшированные транзакции
merkle_tree_data = []


def merkle_tree(haslist):
	global merkle_tree_data
	#когда останется последний элемент, он просто станет корнем, это нерекурентный случай
	if len(merkle_tree_data) == 14:
		merkle_tree_data.insert(0, hashlist[0])
		return merkle_tree_data
	#далее рекурентный случай достаточно тривиален
	for x in range(len(hashlist)-1, -1, -1):
		merkle_tree_data.insert(0, hashlist[x])
	new_hash_list = []
	#такое разделение обусловлено тем, что не стали для определения диапазона генерации использовать логарифмы
	#либо я даун и не смог нормально написать общий range и для случая, когда остается элемента 2 дабл-хэша
	if len(hashlist) == 2:
		additional_arg = hashlib.sha256(hashlist[0]+hashlist[1])
		new_hash_list.append(additional_arg)
	else:
		for y in range(0, len(hashlist)-1, 2):
			additional_arg = hashlib.sha256(hashlist[y]+hashlist[y+1])
			new_hash_list.append(additional_arg)
	merkle_tree(new_hash_list)

