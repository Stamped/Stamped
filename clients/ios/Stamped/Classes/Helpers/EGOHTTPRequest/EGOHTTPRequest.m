//
//  EGOHTTPRequest.m
//  EGOHTTPRequest
//
//  Created by Shaun Harrison on 12/2/09.
//  Copyright (c) 2009-2010 enormego
//
//  Permission is hereby granted, free of charge, to any person obtaining a copy
//  of this software and associated documentation files (the "Software"), to deal
//  in the Software without restriction, including without limitation the rights
//  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
//  copies of the Software, and to permit persons to whom the Software is
//  furnished to do so, subject to the following conditions:
//
//  The above copyright notice and this permission notice shall be included in
//  all copies or substantial portions of the Software.
//
//  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
//  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
//  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
//  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
//  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
//  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
//  THE SOFTWARE.
//

#import "EGOHTTPRequest.h"

static NSMutableArray *__currentRequests;
static dispatch_queue_t __queue;

@interface EGOHTTPRequest ()
+ (void)cleanUpRequest:(EGOHTTPRequest*)request;
+ (dispatch_queue_t)queue;
- (NSURLRequest*)_buildURLRequest;
@end

@implementation EGOHTTPRequest

@synthesize url=_URL;
@synthesize response=_response;
@synthesize timeoutInterval=_timeoutInterval; 
@synthesize error=_error;
@synthesize cancelled=_cancelled;
@synthesize started=_started;
@synthesize finished=_finished;
@synthesize requestMethod=_requestMethod;
@synthesize requestBody=_requestBody;
@synthesize completion=_completion;
@synthesize status=_status;
@synthesize identifier=_identifier;

- (id)initWithURL:(NSURL*)aURL completion:(void(^)(id, NSError *))completion{
	
    if ((self = [super init])) {
        
        _URL = [aURL retain];
        _timeoutInterval = 30;
        _completion = [completion copy];
        
        NSMutableData *data = [[NSMutableData alloc] init];
        _responseData = [data retain];
        [data release];
        
        NSMutableDictionary *dictionary = [[NSMutableDictionary alloc] init];
        _requestHeaders = [dictionary retain];
        [dictionary release];
        
        self.requestMethod = @"GET";
        
    }
    
    return self;
    
}

- (id)initWithURL:(NSURL*)aURL status:(void(^)(id, NSNumber *))status completion:(void(^)(id, NSError *))completion{
    
    if((self = [self initWithURL:aURL completion:completion])){
        _status = [status copy];
    }
    return self;
    
}

- (id)initWithURL:(NSURL *)aURL identifier:(NSString*)identifier completion:(void(^)(id, NSError *))completion{
    
    if ((self = [self initWithURL:aURL completion:completion])) {
        _identifier = [identifier copy];
    }
    return self;
    
}

- (id)initWithURL:(NSURL*)aURL identifier:(NSString*)identifier status:(void(^)(id, NSNumber *))status completion:(void(^)(id, NSError *))completion{
   
    if ((self = [self initWithURL:aURL completion:completion])) {
        _identifier = [identifier copy];
        _status = [status copy];
    }
    return self;
    
}

+ (NSMutableArray*)currentRequests {
    
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        __currentRequests = [[NSMutableArray alloc] init];	

    });
	
	return __currentRequests;
}

+ (dispatch_queue_t)queue {
    
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        __queue = dispatch_queue_create("com.enormego.egohttprequest", NULL );
        dispatch_queue_t priority = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_HIGH,0);
		dispatch_set_target_queue(priority, __queue);
    });
    
    return __queue;
}

- (void)addRequestHeader:(NSString *)header value:(NSString *)value {
	[_requestHeaders setObject:value forKey:header];
}

- (NSURLRequest*)_buildURLRequest {
	if(_started || _cancelled){
        return nil;
    } else {
        _started = YES;
    }

	NSMutableURLRequest *request = [[NSMutableURLRequest alloc] initWithURL:self.url cachePolicy:NSURLRequestReloadIgnoringCacheData timeoutInterval:self.timeoutInterval];
	[request setValue:@"gzip" forHTTPHeaderField:@"Accept-Encoding"];
	
	if(_requestMethod) {
		[request setHTTPMethod:_requestMethod];
	} else {
		[request setHTTPMethod:@"GET"];
	}
	    
	if(_requestBody) {
		[request setHTTPBody:_requestBody];
	}
	
	for(NSString *key in _requestHeaders) {
		[request setValue:[_requestHeaders objectForKey:key] forHTTPHeaderField:key];
	}
	    
    dispatch_sync([[self class] queue], ^{
        [[[self class] currentRequests] addObject:self];
    });
    	
	return [request autorelease];
}

- (void)startAsynchronous {

	NSURLRequest *request = [self _buildURLRequest];
    if(!request) return;
    
    //[[UIApplication sharedApplication] ft_pushNetworkActivity];
    [self performSelectorInBackground:@selector(startConnectionInBackgroundWithRequest:) withObject:request];
    
}

- (void)startSynchronous {
	
    NSURLRequest *request = [self _buildURLRequest];
	if(!request) return;
	
    //[[UIApplication sharedApplication] ft_pushNetworkActivity];
	NSURLResponse *aResponse = nil;
	NSError *anError = nil;
	NSData *responseData = [NSURLConnection sendSynchronousRequest:request returningResponse:&aResponse error:&anError];
	
	[_responseData setData:responseData];
	self.response = aResponse;
	
	if(_error) [_error release];
	
	if(anError) {
		_error = [anError retain];
		
		if(!_cancelled) {
            _completion(self, _error);
		}		
	} else {
		_error = nil;
        
		if(!_cancelled) {
            _completion(self, nil);
		}
	}
	
	_finished = YES;
	[[self class] cleanUpRequest:self];
    
}

- (void)startConnectionInBackgroundWithRequest:(NSURLRequest*)request {
    
	NSAutoreleasePool *pool = [[NSAutoreleasePool alloc] init];
	_backgroundThread = [[NSThread currentThread] retain];
	
	_connection = [[NSURLConnection alloc] initWithRequest:request delegate:self startImmediately:YES];
	
	while(!_cancelled && !_finished) {
		[[NSRunLoop currentRunLoop] runMode:NSDefaultRunLoopMode beforeDate:[NSDate distantFuture]];
	}
	
	if(_cancelled) {
		[_connection cancel];
	}
    
	[_backgroundThread release];
	_backgroundThread = nil;
	
	[_connection release];
	_connection = nil;
	
	[pool release];
    [[self class] cleanUpRequest:self];

}


#pragma mark -
#pragma mark Cancel | Cleanup

+ (void)cleanUpRequest:(EGOHTTPRequest*)request {
    
    dispatch_sync([[self class] queue], ^{
        [[self currentRequests] removeObject:request];
        //[[UIApplication sharedApplication] ft_popNetworkActivity];
    });
    
}

+ (void)cancelRequestsForIdentifier:(NSString*)identifier {
    if (identifier==nil) return;
    
    NSArray *requests = [self currentRequests];
    [requests enumerateObjectsUsingBlock:^(id obj, NSUInteger index, BOOL *stop) {
        EGOHTTPRequest *request = obj;
        if([request.identifier isEqualToString:identifier]) {
            if (![request isCancelled]) {
                [request cancel];
                [[self class] cleanUpRequest:request];
            }
            *stop = YES;
        }
    }];
    	
}

- (void)cancel {
	if(_cancelled) return;
	
    _cancelled = YES;
	_finished = YES;
    self.status=nil;
    self.completion=nil;
}


#pragma mark -
#pragma mark Response Getters

- (NSData*)responseData {
	return _responseData;
}

- (NSString*)responseString {
	NSStringEncoding stringEncoding;
	
	if([self.response textEncodingName].length > 0) {
		stringEncoding = CFStringConvertEncodingToNSStringEncoding(CFStringConvertIANACharSetNameToEncoding((CFStringRef)[self.response textEncodingName]));
	} else {
		stringEncoding = NSUTF8StringEncoding;	
	}
	
	return [[[NSString alloc] initWithData:self.responseData encoding:stringEncoding] autorelease];
}

- (NSDictionary*)responseHeaders {
	if([self.response isKindOfClass:[NSHTTPURLResponse class]]) {
		return [(NSHTTPURLResponse*)self.response allHeaderFields];
	} else {
		return nil;	
	}
}

- (NSInteger)responseStatusCode {
	if([self.response isKindOfClass:[NSHTTPURLResponse class]]) {
		return [(NSHTTPURLResponse*)self.response statusCode];
	} else {
		return -NSNotFound;	
	}
}


#pragma mark -
#pragma mark NSURLConnectionDelegate

- (void)connection:(NSURLConnection *)connection didReceiveData:(NSData *)data {
	if(connection != _connection) return;
	[_responseData appendData:data];   
            
    if (((_status!=nil) && ([[self responseHeaders] objectForKey:@"Content-Length"] !=nil))) {
        CGFloat length = [[[self responseHeaders] objectForKey:@"Content-Length"] floatValue];
        _status(self, [NSNumber numberWithFloat:([_responseData length]/length)]);

    }
    
}

- (void)connection:(NSURLConnection *)connection didReceiveResponse:(NSURLResponse *)response {
	if(connection != _connection) return;

	self.response = response;
}

- (void)connectionDidFinishLoading:(NSURLConnection *)connection {
	if(connection != _connection) return;
    
	if(!_cancelled) {        
        _completion(self, nil);
	}
	
	_finished = YES;
    
}

- (void)connection:(NSURLConnection *)connection didFailWithError:(NSError *)error {
	if(connection != _connection) return;

	[_error release];
	_error = [error retain];
    
	if(!_cancelled) {
        _completion(self, error);
	}
	
	_finished = YES;

}

- (void)connection:(NSURLConnection *)connection didSendBodyData:(NSInteger)bytesWritten totalBytesWritten:(NSInteger)totalBytesWritten totalBytesExpectedToWrite:(NSInteger)totalBytesExpectedToWrite {
    
    if ((_status!=nil)) {
        _status(self, [NSNumber numberWithFloat:totalBytesExpectedToWrite - totalBytesWritten]);
    }

}


#pragma mark -
#pragma mark Dealloc

- (void)dealloc {

    self.status = nil;
    self.completion = nil;
    self.identifier = nil;
    [_response release], _response=nil;
    [_requestMethod release], _requestMethod=nil;
    [_requestBody release], _requestBody=nil;
	[_responseData release]; _responseData=nil;
	[_requestHeaders release], _requestHeaders = nil;
	[_connection release], _connection = nil;
	[_error release], _error = nil;
	[_URL release], _URL = nil;
    
	[super dealloc];
}

@end
