import boto3

def lambda_handler(event, context):
    instancesToHibernate = []
    region = getRegion(event)
    ec2Client = boto3.client('ec2', region_name=region)
    id = getInstanceId(event)

    if id is not None:
        instancesToHibernate.append(id)
        ec2Client.stop_instances(InstanceIds=instancesToHibernate, Hibernate=True)
        print('stopped instances: ' + str(instancesToHibernate) + ' in region ' + region)
    else:
        print('No instance id found')

def getRegion(payload):
    if 'region' in payload:
        region = payload['region']
        return region 
    
    #default to N. Virginia
    return 'us-east-1'

def getInstanceId(payload):
    if 'detail' in payload:
        detail = payload['detail']
        if 'configuration' in detail:
            configuration = detail['configuration']
            if 'metrics' in configuration:
                if len(configuration['metrics']) > 0:
                    firstMetric = configuration['metrics'][0] 
                    if 'metricStat' in firstMetric:
                        metricStat = firstMetric['metricStat']
                        if 'metric' in metricStat:
                            metric = metricStat['metric']
                            if 'dimensions' in metric:
                                dimensions = metric['dimensions']
                                if 'InstanceId' in dimensions:
                                    id = dimensions['InstanceId']
                                    return id
    
    return None