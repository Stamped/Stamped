//
//  STStampDetailHeaderView.h
//  Stamped
//
//  Created by Landon Judkins on 4/2/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "STStamp.h"
#import "STEntity.h"

@interface STStampDetailHeaderView : UIView

-(id)initWithStamp:(id<STStamp>)stamp;
-(id)initWithEntity:(id<STEntity>)entity;

@end
