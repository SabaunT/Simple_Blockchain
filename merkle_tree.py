import hashlib

#list of transactions example
Tx_hashlist1 = ['A1', 'B2', 'C3', 'D4', 'E5', 'F6', 'G7', 'H8']
#hash of each transaction is added to the list below; the lowest leaf is based
Tx_hashlist = [hashlib.sha256(each.encode()).hexdigest() for each in Tx_hashlist1]

#merkle tree presented as an array (list in python)
merkle_tree_data = []

def merkle_tree(hashlist):
	global merkle_tree_data
	#non-recursion case
	if len(merkle_tree_data) == 14:
		merkle_tree_data.insert(0, hashlist[0])
		return merkle_tree_data
	#recursion case
	for x in range(len(hashlist)-1, -1, -1):
		merkle_tree_data.insert(0, hashlist[x])
	new_hash_list = []
	if len(hashlist) == 2:
		additional_arg = hashlist[0]+hashlist[1]
		new_hash_arg = hashlib.sha256(additional_arg.encode()).hexdigest()
		new_hash_list.append(new_hash_arg)
	else:
		for y in range(0, len(hashlist)-1, 2):
			additional_arg = hashlist[y]+hashlist[y+1]
			new_hash_arg = hashlib.sha256(additional_arg.encode()).hexdigest()
			new_hash_list.append(new_hash_arg)
	merkle_tree(new_hash_list)

merkle_tree(Tx_hashlist)
print (merkle_tree_data)
