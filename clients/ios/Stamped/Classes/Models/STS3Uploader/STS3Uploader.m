//
//  STS3Uploader.m
//  Stamped
//
//  Created by Devin Doty on 6/8/12.
//
//

#import "STS3Uploader.h"
#import "ASIHTTPRequest.h"
#import "ASIS3ObjectRequest.h"
#import <RestKit/NSData+MD5.h>

// Amazon S3 Shit. -bons
static NSString* const kS3SecretAccessKey = @"4hqp3tVDt9ALgEFhDTqC4Y1P661uFNjtYqPVu2MW";
static NSString* const kS3AccessKeyID = @"AKIAIRLTXI62SD3BWAHQ";
static NSString* const kS3Bucket = @"stamped.com.static.temp";

@implementation STS3Uploader
@synthesize uploading=_uploading;
@synthesize progress=_progress;
@synthesize filePath;
@synthesize request=_request;

- (void)dealloc {
    self.filePath=nil;
    if (_request) {
        [_request cancel];
        [_request release], _request=nil;
    }
    [super dealloc];
}

- (void)startWithProgress:(STS3UploaderProgress)progress completion:(STS3UploaderCompletion)completion {
    if (_uploading || !filePath) return;
    _uploading = YES;
    
    NSString *key = [NSString stringWithFormat:@"%@-%.0f.jpg", [self.filePath MD5], [[NSDate date] timeIntervalSince1970]];
    NSString *tempPath = [NSString stringWithFormat:@"http://s3.amazonaws.com/stamped.com.static.temp/%@", key];
    ASIS3ObjectRequest *request = [ASIS3ObjectRequest PUTRequestForFile:self.filePath withBucket:kS3Bucket key:key];
    request.secretAccessKey = kS3SecretAccessKey;
    request.accessKey = kS3AccessKeyID;
    request.accessPolicy = ASIS3AccessPolicyPublicRead;
    request.timeOutSeconds = 30;
    request.numberOfTimesToRetryOnTimeout = 2;
    request.mimeType = @"image/jpeg";
    request.shouldAttemptPersistentConnection = NO;
    [request setBytesSentBlock:^(unsigned long long size, unsigned long long total){
        if (progress) {
            progress(size/total);
        }
    }];
    [request setCompletionBlock:^{
        if (completion) {
            completion(tempPath, YES);
        }
        [_request release], _request=nil;
    }];
    [request setFailedBlock:^{
        if (completion) {
            completion(tempPath, NO);
        }
        [_request release], _request=nil;
    }];
    [ASIS3Request setShouldUpdateNetworkActivityIndicator:NO];
    [request startAsynchronous];
    _request = [request retain];
    
}

- (void)cancel {
    
    if (_request) {
        [_request cancel];
        [_request release], _request=nil;
    }
    _uploading = NO;
    
}

@end
