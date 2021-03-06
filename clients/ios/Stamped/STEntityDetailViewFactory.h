//
//  STEntityDetailViewFactory.h
//  Stamped
//
//  Created by Landon Judkins on 3/23/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STViewDelegate.h"
#import "STEntityDetail.h"
#import "STEntityDetailComponentFactory.h"

@interface STEntityDetailViewFactory : NSObject <STEntityDetailComponentFactory>

- (id)initWithContext:(STActionContext*)context;

@end
