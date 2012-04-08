//
//  STRestKitLoader.h
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>

@interface STRestKitLoader : NSObject

- (void)loadWithPath:(NSString*)path 
                post:(BOOL)post
              params:(NSDictionary*)params 
             mapping:(RKObjectMapping*)mapping 
         andCallback:(void(^)(NSArray*,NSError*))block;

- (void)loadOneWithPath:(NSString*)path
                   post:(BOOL)post
                 params:(NSDictionary*)params 
                mapping:(RKObjectMapping*)mapping 
            andCallback:(void(^)(id,NSError*))block;

+ (STRestKitLoader*)sharedInstance;

@end
