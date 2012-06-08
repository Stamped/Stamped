//
//  STBadgeBarButtonItem.h
//  Stamped
//
//  Created by Devin Doty on 6/8/12.
//
//

#import <Foundation/Foundation.h>
#import "STNavigationItem.h"

@interface STBadgeBarButtonItem : STNavigationItem {
    UIView *_countView;
    UILabel *_countLabel;
}

@end
