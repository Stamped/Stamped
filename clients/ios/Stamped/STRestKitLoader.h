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
                  authenticated:(BOOL)authenticated
                         params:(NSDictionary*)params 
                        mapping:(RKObjectMapping*)mapping 
                    andCallback:(void(^)(NSArray* results, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)loadOneWithPath:(NSString*)path
                              post:(BOOL)post 
                     authenticated:(BOOL)authenticated
                            params:(NSDictionary*)params 
                           mapping:(RKObjectMapping*)mapping 
                       andCallback:(void(^)(id result, NSError* error, STCancellation* cancellation))block;

- (void)authenticate;
- (void)refreshToken;
- (void)logout;

+ (STRestKitLoader*)sharedInstance;

@end
