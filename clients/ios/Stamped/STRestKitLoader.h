//
//  STRestKitLoader.h
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STCancellation.h"

@interface STRestKitLoader : NSObject

- (STCancellation*)loadWithPath:(NSString*)path 
                           post:(BOOL)post
                         params:(NSDictionary*)params 
                        mapping:(RKObjectMapping*)mapping 
                    andCallback:(void(^)(NSArray* results, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)loadOneWithPath:(NSString*)path
                              post:(BOOL)post
                            params:(NSDictionary*)params 
                           mapping:(RKObjectMapping*)mapping 
                       andCallback:(void(^)(id result, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)booleanWithPath:(NSString*)path
                              post:(BOOL)post
                            params:(NSDictionary*)params
                       andCallback:(void(^)(BOOL boolean, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)loadWithURL:(NSString*)url 
                          post:(BOOL)post
                        params:(NSDictionary*)params 
                       mapping:(RKObjectMapping*)mapping 
                   andCallback:(void(^)(NSArray* results, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)loadOneWithURL:(NSString*)url
                             post:(BOOL)post
                           params:(NSDictionary*)params 
                          mapping:(RKObjectMapping*)mapping 
                      andCallback:(void(^)(id result, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)booleanWithURL:(NSString*)url
                             post:(BOOL)post
                           params:(NSDictionary*)params
                      andCallback:(void(^)(BOOL boolean, NSError* error, STCancellation* cancellation))block;

+ (STRestKitLoader*)sharedInstance;

@end
