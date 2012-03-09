//
//  STEntityDetailFactory.h
//  Stamped
//
//  Created by Landon Judkins on 3/9/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STEntityDetail.h"
#import "STFactoryDelegate.h"

@interface STEntityDetailFactory : NSObject

- (void)createWithEntityId:(NSString*)entityID delegate:(id<STFactoryDelegate>)delegate label:(id)label;

@end
