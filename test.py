import urlparse
a = "https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&tn=baidu&wd=python%20url%E8%8E%B7%E5%8F%96get%E5%8F%82%E6%95%B0&oq=python%2520%25E8%25BD%25AC%25E6%258D%25A2%25E5%25B0%258F%25E5%2586%2599&rsv_pq=d5d105a700012450&rsv_t=ca036rDPOjdJTfFBPC8o2Pvv6T%2BMA1U4C00JkjjH6cKCHw53RJa9RnreSCU&rqlang=cn&rsv_enter=1&inputT=5488&rsv_sug3=109&rsv_sug1=69&rsv_sug7=100&rsv_sug2=0&rsv_sug4=5488"

query = urlparse.urlparse(a).query
prarm = dict([(k,v[0]) for k,v in urlparse.parse_qs(query).items()])
b=1
