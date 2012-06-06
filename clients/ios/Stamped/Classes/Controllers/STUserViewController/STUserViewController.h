//
//  STUserViewController.h
//  Stamped
//
//  Created by Devin Doty on 6/5/12.
//
//

#import <UIKit/UIKit.h>
#import "STRestViewController.h"

@class STSimpleUserDetail;
@interface STUserViewController : STRestViewController;

- (id)initWithUserIdentifier:(NSString*)identifier;
- (id)initWithUser:(id)user;


@end
