# Common global variables and functions
NODES_PER_ZONE = 3             # likely a 6-node cluster
MAX_NODES = 9                  # upper limit on node count
NODE_PREFIX = "cassnode"       # all nodenames begin with this
IMAGE = "debian-7"             # either debian-6, debian-7, or centos-6
MACHINE_TYPE = "n1-standard-1" # basic machine type
API_VERSION = "v1beta15"       # GCE API version
WAIT_MAX = 10                  # max wait for startup-scripts

# Internal data structure for the cluster is a dict by 'zone', with a list      
# of dicts containing 'name' and 'ip'                                           
# e.g.                                                                          
# cluster['us-central1-a'] = [                                                  
#   {'name': 'cassnode-a-0', 'ip': '192.168.72.3'},                             
#   {'name': 'cassnode-a-1', 'ip': '192.168.112.92'}                            
# ]                                                                             
def get_cluster():                                                               
  """Return the program data structure of a cluster"""
  cluster = {}                                                                  
  pattern = "name eq '%s.*'" % NODE_PREFIX                                      
  csv = subprocess.check_output(["gcutil",                                      
      "--service_version=%s" % API_VERSION, "--format=csv", "listinstances",      
      "--filter=%s" % pattern], stderr=NULL).split('\n')                          
  for line in csv:                                                              
    p = line.split(',')                                                     
    if p[0].startswith(NODE_PREFIX):                                        
      if cluster.has_key(p[7]):                                             
        cluster[p[7]].append({'name':p[0], 'ip':p[4], 'zone':p[7]})               
      else:                                                                     
        cluster[p[7]] = [{'name':p[0], 'ip':p[4], 'zone':p[7]}]                   
  return cluster                                                                

# Return the image URL that matches IMAGE
def get_image_path():
  """Return the image URL that matches IMAGE"""
  imagePath = None
  csv = subprocess.check_output(["gcutil",
      "--service_version=%s" % API_VERSION, "--format=csv", "listimages",
      "--filter", "status eq READY"], stderr=NULL).split('\n')[1:-1]
  for line in csv:
    name = line.split(',')[0]
    path = name.split('/')
    if path[4].startswith(IMAGE):
      imagePath = name 
  return imagePath
