//
//  EGOHTTPRequest.h
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

#import <Foundation/Foundation.h>

@interface EGOHTTPRequest : NSObject {
@private
	NSURL *_URL;
	NSError *_error;
	NSURLResponse *_response;
	NSMutableData *_responseData;
	NSURLConnection *_connection;
	NSMutableDictionary *_requestHeaders;
    
	NSTimeInterval _timeoutInterval;
    
	BOOL _started;
	BOOL _finished;
	BOOL _cancelled;
	
	NSThread *_backgroundThread;
	
	NSString *_requestMethod;
	NSData *_requestBody;
    
    void(^_completion)(id request, NSError *error);
    void(^_status)(id request, NSNumber *complete); //URL request status, will get called if header contains size
    NSString *_identifier;
    
}

+ (NSMutableArray*)currentRequests;
+ (void)cancelRequestsForIdentifier:(NSString*)identifier;

- (id)initWithURL:(NSURL*)aURL completion:(void(^)(id, NSError *))completion;

/*
 * Request with optional status callback, will only get called if headers have 'Content-Lenght'
 */
- (id)initWithURL:(NSURL*)aURL status:(void(^)(id, NSNumber *))status completion:(void(^)(id, NSError *))completion;

/*
 * Identifier is used to cancel a request
 */
- (id)initWithURL:(NSURL*)aURL identifier:(NSString*)identifier completion:(void(^)(id, NSError *))completion;
- (id)initWithURL:(NSURL*)aURL identifier:(NSString*)identifier status:(void(^)(id, NSNumber *))status completion:(void(^)(id, NSError *))completion;

- (void)addRequestHeader:(NSString *)header value:(NSString *)value;

- (void)startAsynchronous;
- (void)startSynchronous;
- (void)cancel;

@property(nonatomic,copy) void(^completion)(id request, NSError *error);
@property(nonatomic,copy) void(^status)(id request, NSNumber *complete);
@property(nonatomic,copy) NSString *identifier;

@property(nonatomic,retain) NSString *requestMethod; // Default: GET
@property(nonatomic,retain) NSData *requestBody;

@property(nonatomic,readonly) NSData *responseData;
@property(nonatomic,readonly) NSString *responseString;
@property(nonatomic,readonly) NSInteger responseStatusCode;
@property(nonatomic,readonly) NSDictionary *responseHeaders;

@property(nonatomic,readonly,getter=URL) NSURL *url;
@property(nonatomic,readonly) NSError *error;
@property(nonatomic,readonly,getter=isStarted) BOOL started;
@property(nonatomic,readonly,getter=isFinished) BOOL finished;
@property(nonatomic,readonly,getter=isCancelled) BOOL cancelled;

@property(nonatomic,retain) NSURLResponse *response;
@property(nonatomic,assign) NSTimeInterval timeoutInterval; // Default is 60 seconds

@end