//
//  STEntityDetailFactory.h
//  Stamped
//
//  Created by Landon Judkins on 3/9/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STEntityDetail.h"

@interface STEntityDetailFactory : NSObject

- (NSOperation*)entityDetailCreatorWithEntityId:(NSString*)anEntityID andCallbackBlock:(void (^)(id<STEntityDetail>))aBlock;
- (NSOperation*)entityDetailCreatorWithSearchId:(NSString*)aSearchID andCallbackBlock:(void (^)(id<STEntityDetail>))aBlock;

+ (STEntityDetailFactory*)sharedFactory;

@end
