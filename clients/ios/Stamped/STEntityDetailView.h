//
//  STEntityDetailView.h
//  Stamped
//
//  Created by Landon Judkins on 3/26/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STViewContainer.h"
#import "STEntityDetail.h"

@interface STEntityDetailView : STViewContainer

- (id)initWithDelegate:(id<STViewDelegate>)delegate andEntityDetail:(id<STEntityDetail>)anEntityDetail;

@end
