//
//  STMenuPopUp.h
//  Stamped
//
//  Created by Landon Judkins on 3/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "STMenu.h"
#import "STEntityDetail.h"

@interface STMenuPopUp : UIView

- (id)initWithEntityDetail:(id<STEntityDetail>)entityDetail andMenu:(id<STMenu>)menu;

@end
