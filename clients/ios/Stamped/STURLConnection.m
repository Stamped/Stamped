//
//  STURLConnection.m
//  Stamped
//
//  Created by Landon Judkins on 4/26/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STURLConnection.h"
#import "Util.h"

@interface STURLConnection () <STCancellationDelegate>

@property (nonatomic, readonly, retain) NSURLConnection* connection;
@property (nonatomic, readonly, retain) NSMutableData* data;
@property (nonatomic, readonly, copy) void(^callback)(NSData* data, NSError* error, STCancellation* cancellation);

@end

@implementation STURLConnection

@synthesize cancellation = cancellation_;
@synthesize connection = connection_;
@synthesize data = data_;
@synthesize callback = callback_;

- (id)initWithURL:(NSURL*)url andCallback:(void(^)(NSData* data, NSError* error, STCancellation* cancellation))block {
  self = [super init];
  if (self) {
    [self retain];
    cancellation_ = [[STCancellation cancellationWithDelegate:self] retain];
    data_ = [[NSMutableData alloc] init];
    callback_ = [block copy];
    [Util executeOnMainThread:^{
      NSURLRequest* request = [NSURLRequest requestWithURL:url];
      connection_ = [[NSURLConnection connectionWithRequest:request delegate:self] retain];
    }];
  }
  return self;
}

- (void)dealloc
{
  [cancellation_ release];
  [connection_ release];
  [data_ release];
  [callback_ release];
  [super dealloc];
}

- (void)cancellationWasCancelled:(STCancellation *)cancellation {
  [self.connection cancel];
  [self autorelease];
}

+ (STCancellation*)cancellationWithURL:(NSURL*)url andCallback:(void(^)(NSData* data, NSError* error, STCancellation* cancellation))block {
  STURLConnection* connection = [[[STURLConnection alloc] initWithURL:url andCallback:block] autorelease];
  return connection.cancellation;
}


#pragma mark - NSURLConnectionDelegate methods.

- (void)connection:(NSURLConnection*)connection didReceiveData:(NSData*)data {
  [self.data appendData:data];
}

- (void)connection:(NSURLConnection*)connection didFailWithError:(NSError*)error {
  if (!self.cancellation.cancelled) {
    self.callback(nil, error, self.cancellation);
  }
  [self autorelease];
}

- (void)connectionDidFinishLoading:(NSURLConnection*)connection {
  if (!self.cancellation.cancelled) {
    self.callback(self.data, nil, self.cancellation);
  }
  [self autorelease];
}
@end
