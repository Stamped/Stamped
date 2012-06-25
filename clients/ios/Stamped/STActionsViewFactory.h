//
//  STActionsViewFactory.h
//  Stamped
//
//  Created by Landon Judkins on 3/13/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STActionItem.h"
#import "STViewDelegate.h"
#import "STAEntityDetailComponentFactory.h"

@interface STActionsViewFactory : STAEntityDetailComponentFactory

+ (UIView*)moreInformationEntityDetail:(id<STEntityDetail>)entityDetail andDelegate:(id<STViewDelegate>)delegate;

@end
