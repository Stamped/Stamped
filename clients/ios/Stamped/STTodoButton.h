//
//  STTodoButton.h
//  Stamped
//
//  Created by Landon Judkins on 4/4/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STAStampButton.h"
#import "STStamp.h"
#import "STEntity.h"

@interface STTodoButton : STAStampButton

- (id)initWithStamp:(id<STStamp>)stamp;
- (id)initWithEntityID:(NSString*)entityID;

@end
