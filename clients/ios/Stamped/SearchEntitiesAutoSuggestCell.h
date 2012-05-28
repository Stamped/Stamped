//
//  SearchEntitiesAutoSuggestCell.h
//  Stamped
//
//  Created by Andrew Bonventre on 11/2/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface SearchEntitiesAutoSuggestCell : UITableViewCell

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier;

@property (nonatomic, readonly) UILabel* customTextLabel;

@end
