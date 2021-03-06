//
//  STHeaderViewFactory.h
//  Stamped
//
//  Created by Landon Judkins on 3/13/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STEntityDetail.h"
#import "STViewDelegate.h"
#import "STAEntityDetailComponentFactory.h"

@interface STHeaderViewFactory : STAEntityDetailComponentFactory

- (id)initWithStyle:(NSString*)style;

@end
