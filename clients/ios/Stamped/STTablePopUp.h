//
//  STTablePopUp.h
//  Stamped
//
//  Created by Landon Judkins on 4/10/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STViewDelegate.h"
#import "STViewContainer.h"

@interface STTablePopUp : UIView <STViewDelegate, UITableViewDelegate, UITableViewDataSource>

- (id)initWithFrame:(CGRect)frame;
- (id)init;

@property (nonatomic, readonly, retain) UIView* header;
@property (nonatomic, readonly, retain) UIView* footer;
@property (nonatomic, readonly, retain) UITableView* table;

@end
